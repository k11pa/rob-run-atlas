"""Builds dist/data.js and dist/db.js from Supabase. The database is the source of truth and is only read.

Usage: build-from-db.py [--out DIR]
Everything is validated before writing, so a failed build leaves the previous files in place.
"""
import collections, json, os, pathlib, re, struct, sys
import psycopg
from psycopg.rows import dict_row

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
REPORT = ROOT / "docs/DB_BUILD_REPORT_RU.md"
HUB = dict(x_min=-27.0, x_max=24.0, z_min=24.0, z_max=54.0)  # outputs/rob-run-research/map-assets/hub/hub_projection_and_pois.json
# Broken or mismatched game localization: show the native enum name, never an invented translation.
BROKEN_TYPE_NAMES = {"д", "Локализация не найдена", "Деревянная статуэтка", "Касса"}
# InventoryItemSellPriceModifier rows, indexed like attribute sell-price-modifier-index. Not in the database yet:
# decoded from work/references.dat offset 361085 and matching InventoryItemSellPriceModifiers..cctor, build 26342425.
SELL_MODIFIERS = [0.4, 0.1, 0.1, 0.1, 0.1, 0.0, 0.2, 0.1, 1.0]
# Game data leaves this vendor's name as its raw ID.
VENDOR_NAMES = {"city_trader_car_parts": "Торговец автозапчастями"}
# Same generic name for many keys: the place comes from each item's own description.
KEY_NAMES = {"Ключ от сейфа", "Ключ от комнаты"}
# Every language gives these the name and description of the storage building (storage_building_1).
WRONG_LOCALIZATION = {"crypto_farm_1", "crypto_workbench_1", "video_card_1", "broken_video_card", "crypto_wallet", "crypto_workbench_speedup_upgrade", "crypto_workbench_cooling_upgrade"}
# Texts that describe the method, not game data; the database has no place for them.
POINT_LOOT_SOURCE = "native_city_builder_plus_public_references"
PURCHASE_SOURCE = "TraderInventoryDescription"
CONVERSION_SOURCE = "CumulativeItemDescription + inventory reference + ContainerDescription rewards"
ACQUISITION_NOTES = {
    "tiers": "TierDescription enum: tier_1/2/3 indices 0/1/2; stock keys are references to this enum.",
    "vendorUnlock": "VendorTreeNodeDescription identifies the item unlocked. Costs, predecessor nodes and realm-dependent parameters are not yet decoded.",
    "scope": "Purchasing stock and barter are acquisition routes, never proof of a container drop. No unverified key/door/safe edges are included.",
}
AUDIT_NOTE = "Наличие источника не означает, что восстановлены все ограничения входа, предыдущие узлы торговца или случайные пулы."

sys.stdout.reconfigure(encoding="utf-8")
out_dir = pathlib.Path(sys.argv[sys.argv.index("--out") + 1]).resolve() if "--out" in sys.argv else DIST


def env_url():
    env = ROOT / ".env"
    if not env.exists():
        sys.exit("Нет файла .env с SUPABASE_DB_URL")
    for line in env.read_text("utf-8-sig").splitlines():
        if line.startswith("SUPABASE_DB_URL="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("В .env нет SUPABASE_DB_URL")


conn = psycopg.connect(env_url(), connect_timeout=20, row_factory=dict_row,
                       options="-c default_transaction_read_only=on -c statement_timeout=60000 -c search_path=robrun_wiki")
conn.read_only = True


def q(sql):
    with conn.cursor() as c:
        c.execute(sql)
        return c.fetchall()


def num(v):
    if v is None:
        return None
    v = float(v)
    return int(v) if v.is_integer() else v


def sell_price(base, index):
    """InventoryItemSellPriceModifier.GetSellPrice: float32 product, rounded half to even."""
    f32 = lambda v: struct.unpack("f", struct.pack("f", v))[0]
    return round(f32(f32(base) * f32(SELL_MODIFIERS[index])))


def key_place(description):
    """'Открывает левую скрытую комнату на заправке района Даунтаун.' -> 'левая, на заправке района Даунтаун'"""
    text = re.sub(r"<[^>]+>", "", description).strip().rstrip(".").removeprefix("Открывает ")
    for prefix, label in (("сейф ", ""), ("запертую комнату ", ""), ("левую скрытую комнату ", "левая, "), ("правую скрытую комнату ", "правая, "), ("VIP комнату ", "VIP, ")):
        if text.startswith(prefix):
            return label + text.removeprefix(prefix)
    return text


def group(rows, key):
    out = collections.defaultdict(list)
    for r in rows:
        out[r[key]].append(r)
    return out


patches = q("select game_build from patches order by id desc")
if not patches:
    sys.exit("В таблице patches нет сборки")
meta = q("select * from cfg_map_metadata")[0]
hub_meta = q("select * from cfg_hub_metadata")[0]

# ---------- items
rarities = q("select id, native_enum_value n, name_ru, name_en, hex_color from rarities order by native_enum_value")
rarity_by_id = {r["id"]: r for r in rarities}
attrs = collections.defaultdict(dict)
for r in q("select v.item_id, a.slug, v.value_number n, v.value_boolean b from attribute_values v join attributes a on a.id=v.attribute_id where a.slug in ('base-price','cells-x','cells-y','sell-available','sell-price-modifier-index','stack-size','armor-segments','armor-blocking-rate')"):
    attrs[r["item_id"]][r["slug"]] = r["b"] if r["b"] is not None else num(r["n"])
names = collections.defaultdict(dict)
for r in q("select t.item_id, l.code, t.name, t.description from item_translations t join languages l on l.id=t.language_id"):
    names[r["item_id"]][r["code"]] = r
item_rows = q("""select i.*, it.slug type_id, it.native_name type_native, coalesce(tt.name, it.name_ru) type_name from items i join item_types it on it.id=i.item_type_id
  left join item_type_translations tt on tt.item_type_id=it.id and tt.language_id=(select id from languages where code='ru') order by i.native_index""")
gid = {r["id"]: r["game_id"] for r in item_rows}
items = []
for r in item_rows:
    a, ru, rarity = attrs[r["id"]], names[r["id"]].get("ru"), rarity_by_id[r["rarity_id"]]
    if not ru:
        sys.exit(f"У предмета {r['game_id']} нет русского названия")
    items.append({"id": r["game_id"], "name": ru["name"], "description": ru["description"], "rarity": rarity["n"], "rarityName": rarity["name_en"],
                  "price": a.get("base-price"), "sellAvailable": a.get("sell-available"), "icon": re.sub(r"^media/", "assets/", r["icon_path"] or ""),
                  "cells": [a.get("cells-x"), a.get("cells-y")], "index": r["native_index"]})
counts = collections.Counter(i["rarity"] for i in items)

# ---------- points
loot = group(q("""select a.point_id, i.game_id, a.quantity_min, a.quantity_max, e.steps_min, e.steps_max, k.native_name source from loot_point_entries e
  join acquisition_sources a on a.id=e.acquisition_source_id join items i on i.id=a.item_id join loot_reference_kinds k on k.id=e.reference_kind_id order by e.id"""), "point_id")
required = group(q("""select o.loot_point_id point_id, i.game_id, r.requirement_source, o.access_kind, t.slug type from access_requirement_items x join items i on i.id=x.item_id
  join access_requirements r on r.id=x.requirement_id join access_objects o on o.id=r.access_object_id join access_object_types t on t.id=o.object_type_id order by x.id"""), "point_id")
containers = {r["point_id"]: r for r in q("""select c.id cid, c.point_id, t.native_id, t.native_index, c.drill_allowed, c.drill_time_ms, i.game_id drill_item from loot_point_containers c
  join container_types t on t.id=c.container_type_id left join items i on i.id=c.drill_item_id""")}
rewards = group(q("select container_id, native_type_index, points from container_progress_rewards order by id"), "container_id")
point_rows = q("""select p.id pid, p.entity_id, p.world_x, p.world_y, p.world_z, p.spawn_probability, pt.slug cat, l.name_ru building, l.name_en building_key, rg.name_ru region, d.*, s.native_name status
  from loot_points p join loot_point_details d on d.point_id=p.id join point_types pt on pt.id=p.point_type_id left join locations l on l.id=p.location_id
  left join map_regions rg on rg.id=d.region_id left join loot_statuses s on s.id=d.loot_status_id order by p.id""")
entity = {r["pid"]: r["entity_id"] for r in point_rows}
points = []
for r in point_rows:
    pid = r["pid"]
    p = {"id": r["entity_id"], "cat": r["cat"], "name": r["name_ru"], "building": r["building"], "region": r["region"], "px": num(r["map_px"]), "py": num(r["map_py"]),
         "height": round(float(r["world_y"]), 3 if r["cat"] in ("access", "actions") else 2), "group": r["group_key"], "sceneName": r["scene_object_name"], "sourcePath": r["source_path"],
         "x": num(r["world_x"]), "z": num(r["world_z"]), "buildingKey": r["building_key"],
         "loot": [{"id": e["game_id"], "amountMin": e["quantity_min"], "amountMax": e["quantity_max"], **({"stepsMin": e["steps_min"], "stepsMax": e["steps_max"]} if e["steps_min"] is not None else {}), "source": e["source"]} for e in loot.get(pid, [])],
         "spawnProbability": num(r["spawn_probability"])}
    if r["status"]:
        p["lootStatus"] = r["status"]
    for key, col in (("nodeLootId", "node_loot_id"), ("nodeLocked", "node_locked"), ("lootObjectId", "loot_object_id"), ("viewPathId", "view_path_id"), ("unlockTimeMs", "unlock_time_ms"), ("setToolTimeMs", "set_tool_time_ms"), ("actionPoints", "action_points")):
        if r[col] is not None:
            p[key] = num(r[col]) if key in ("viewPathId", "unlockTimeMs", "setToolTimeMs", "actionPoints") else r[col]
    req = required.get(pid, [])
    if req or r["cat"] in ("containers", "access", "actions"):
        p["requiredItems"] = [x["game_id"] for x in req]
    c = containers.get(pid)
    if c:
        p.update(containerTypeId=c["native_id"], containerTypeIndex=c["native_index"], drillAllowed=c["drill_allowed"], drillTimeMs=c["drill_time_ms"], drillItem=c["drill_item"],
                 cumulativeRewards=[{"type_index": x["native_type_index"], "points": x["points"]} for x in rewards.get(c["cid"], [])])
    if r["cat"] == "access" and req:
        p.update(requirementSource=req[0]["requirement_source"], accessKind=req[0]["access_kind"])
    points.append(p)

# ---------- buildings and hub
links = group(q("select location_id, i.game_id, link_kind from location_item_links x join items i on i.id=x.item_id order by x.id"), "location_id")
building_rows = q("""select d.*, l.name_ru, l.name_en, l.slug loc_slug, s.slug scene, rg.name_ru region from location_details d join locations l on l.id=d.location_id join scenes s on s.id=l.scene_id
  left join map_regions rg on rg.id=d.region_id order by d.native_building_id""")
buildings = [{"id": r["native_building_id"], "key": r["name_en"], "name": r["name_ru"], "title": r["title_ru"], "description": r["description_ru"], "px": num(r["map_px"]), "py": num(r["map_py"]),
              "x": num(r["world_x"]), "z": num(r["world_z"]), "region": r["region"], "icon": r["icon_path"], "rewards": [x["game_id"] for x in links.get(r["location_id"], []) if x["link_kind"] == "advertised_reward"],
              "activities": r["activity_indices"] or [], "rewardStatus": r["reward_status"], "pointCount": r["point_count"], "knownItemIds": [x["game_id"] for x in links.get(r["location_id"], []) if x["link_kind"] == "known_item"],
              "decodedPointCount": r["decoded_point_count"]} for r in building_rows if r["scene"] == "city"]
shop = next(r for r in building_rows if r["scene"] == "hub")
hub = {"width": num(hub_meta["f_width"]), "height": num(hub_meta["f_height"]), "mapAsset": hub_meta["f_mapasset"], "kind": hub_meta["f_kind"],
       "shop": {"id": shop["loc_slug"].replace("-", "_"), "name": shop["title_ru"], "entityId": shop["native_building_id"], "x": num(shop["world_x"]), "y": num(shop["world_y"]), "z": num(shop["world_z"]),
                "px": num(shop["map_px"]), "py": num(shop["map_py"]), "icon": shop["icon_path"]},
       "landmarks": [{"name": r["name_ru"], "px": num(r["map_px"]), "py": num(r["map_py"])} for r in q("select l.* from map_landmarks l join scenes s on s.id=l.scene_id where s.slug='hub' order by l.id")]}

# ---------- recipes and acquisition
recipes = q("select r.id, r.game_recipe_id gid, r.result_item_id res, t.slug type from recipes r join recipe_types t on t.id=r.recipe_type_id order by r.id")
ingredients = group(q("select recipe_id, item_id, quantity from recipe_ingredients order by id"), "recipe_id")
barter = [{"id": r["gid"], "ingredients": [{"id": gid[x["item_id"]], "amount": num(x["quantity"])} for x in ingredients.get(r["id"], [])], "result": gid[r["res"]]} for r in recipes if r["type"] == "barter"]

terms = collections.defaultdict(dict)
for r in q("select t.offer_id, k.slug, t.value_number n, t.value_boolean b, t.value_text x from offer_terms t join trade_term_kinds k on k.id=t.term_kind_id"):
    terms[r["offer_id"]][r["slug"]] = r["b"] if r["b"] is not None else r["x"] if r["x"] is not None else num(r["n"])
unlock_terms = collections.defaultdict(dict)
for r in q("select t.unlock_rule_id, k.slug, t.value_number n, t.value_text x from unlock_rule_terms t join trade_term_kinds k on k.id=t.term_kind_id"):
    unlock_terms[r["unlock_rule_id"]][r["slug"]] = r["x"] if r["x"] is not None else num(r["n"])
unlock_costs = group(q("select unlock_rule_id, item_id, quantity from unlock_costs order by id"), "unlock_rule_id")
unlock_rules = {r["id"]: r for r in q("select id, predecessors_resolved from unlock_rules")}
acquisition = {}
empty = lambda: {"purchases": [], "barters": [], "usedInBarters": [], "points": [], "usedForDoors": [], "conversions": [], "fills": [], "usedForContainers": []}
for i in items:
    acquisition[i["id"]] = empty()
for r in q("""select o.id, o.item_id, v.game_id vid, v.name_ru vname, t.ordinal tier, o.role_restricted, o.unlock_rule_id from vendor_offers o join vendors v on v.id=o.vendor_id
  left join world_tiers t on t.id=o.world_tier_id order by o.id"""):
    t = terms[r["id"]]
    p = {"vendorId": r["vid"], "vendorName": VENDOR_NAMES.get(r["vid"], r["vname"]), "tier": r["tier"], "vendorTreeLocked": t.get("vendor-tree-locked"), "unlockNode": t.get("unlock-node"), "buyPriceModifier": t.get("buy-price-modifier"),
         "roleRestricted": r["role_restricted"], "source": PURCHASE_SOURCE}
    u = r["unlock_rule_id"]
    if u:
        ut = unlock_terms[u]
        p["unlock"] = {"ingredients": [{"id": gid[x["item_id"]], "amount": num(x["quantity"])} for x in unlock_costs.get(u, [])], "coins": ut.get("unlock-coins"), "requiredYears": ut.get("unlock-required-years"),
                       "predecessorsResolved": unlock_rules[u]["predecessors_resolved"], "source": ut.get("unlock-provenance")}
    acquisition[gid[r["item_id"]]]["purchases"].append(p)
for r in recipes:
    if r["type"] == "barter":
        acquisition[gid[r["res"]]]["barters"].append(r["gid"])
        for x in ingredients.get(r["id"], []):
            used = acquisition[gid[x["item_id"]]]["usedInBarters"]
            if r["gid"] not in used:
                used.append(r["gid"])
for r in q("select a.item_id, a.point_id from acquisition_sources a join acquisition_methods m on m.id=a.method_id where m.slug='fixed-loot' order by a.id"):
    acquisition[gid[r["item_id"]]]["points"].append(entity[r["point_id"]])
for p in points:
    for x in p.get("requiredItems") or []:
        if p["cat"] == "access":
            acquisition[x]["usedForDoors"].append(p["id"])
        elif p["cat"] == "containers":
            acquisition[x]["usedForContainers"].append(p["id"])
    if p.get("drillItem"):
        acquisition[p["drillItem"]]["usedForContainers"].append(p["id"])
sources = group(q("select recipe_id, point_id, points_per_action pts from progress_sources order by id"), "recipe_id")
recipe_by_id = {r["id"]: r for r in recipes}
rule_rows = q("select p.*, t.native_type_id from progress_rules p join progress_types t on t.id=p.progress_type_id order by p.id")
for r in rule_rows:
    rc = recipe_by_id[r["recipe_id"]]
    cv = {"id": rc["gid"], "input": gid[r["item_id"]], "result": gid[rc["res"]], "maxPoints": num(r["max_points"]), "typeId": r["native_type_id"], "action": r["action_ru"], "authorityLevel": r["authority_level"],
          "actionPoints": [{"pointId": entity[x["point_id"]], "points": num(x["pts"])} for x in sources.get(r["recipe_id"], [])], "source": CONVERSION_SOURCE, "notes": r["notes"]}
    acquisition[cv["result"]]["conversions"].append(cv)
    acquisition[cv["input"]]["fills"].append(cv)
for r in q("select game_id, has_source, dependencies, unknown_dependencies, cycles, access_complete from acquisition_audit"):
    acquisition[r["game_id"]]["audit"] = {"hasSource": r["has_source"], "unknownDependencies": r["unknown_dependencies"] or [], "cycles": r["cycles"] or [], "dependencies": r["dependencies"] or [], "accessComplete": r["access_complete"]}
steps = group(q("select * from route_steps order by position"), "route_id")
step_items = group(q("select step_id, item_id from route_step_items order by id"), "step_id")
step_points = group(q("select step_id, point_id from route_step_points order by id"), "step_id")
route_required = group(q("select route_id, item_id from route_required_items order by id"), "route_id")
route_evidence = group(q("select route_id, text_en from route_evidence_lines order by position"), "route_id")
for r in q("select * from acquisition_routes order by id"):
    out_steps = []
    for s in steps.get(r["id"], []):
        st = {"title": s["title_ru"], "text": s["instruction_ru"]}
        if step_items.get(s["id"]):
            st["items"] = [gid[x["item_id"]] for x in step_items[s["id"]]]
        ps = [entity[x["point_id"]] for x in step_points.get(s["id"], [])]
        if len(ps) == 1:
            st["pointId"] = ps[0]
        elif ps:
            st["pointIds"] = ps
        out_steps.append(st)
    acquisition[gid[r["item_id"]]].setdefault("routes", []).append({"id": r["native_route_id"], "title": r["title_ru"], "requiredItems": [gid[x["item_id"]] for x in route_required.get(r["id"], [])],
        "gatePointId": entity.get(r["gate_point_id"]), "steps": out_steps, "note": r["notes"], "evidence": [x["text_en"] for x in route_evidence.get(r["id"], [])], "scope": r["scope_note"]})
with_source = sum(v["audit"]["hasSource"] for v in acquisition.values())

# ---------- corrections to game texts, listed in the report
for i in items:
    g = acquisition[i["id"]]
    levels = [c["authorityLevel"] for c in g["fills"] + g["conversions"] if c["authorityLevel"] is not None]
    if levels:
        i["description"] = i["description"].replace("{0}", str(levels[0]))
    if i["name"] in KEY_NAMES:
        i["name"] = f'{i["name"]} · {key_place(i["description"])}'
    if i["id"] in WRONG_LOCALIZATION:
        i["name"], i["description"] = i["id"], "В локализации игры этому предмету ошибочно заданы название и описание склада, поэтому показано его внутреннее имя."

atlas = {"points": points, "buildings": buildings, "items": items, "build": str(patches[0]["game_build"]), "date": meta["f_date"], "width": num(meta["f_width"]), "height": num(meta["f_height"]), "mapAsset": meta["f_mapasset"],
         "mapSource": meta["f_mapsource"], "referenceHash": meta["f_referencehash"],
         "rarities": [{"id": r["n"], "name": r["name_ru"], "color": r["hex_color"], "count": counts[r["n"]]} for r in rarities], "shops": [], "barterRecipes": barter,
         "authorityLevels": [{"level": r["level"], "lootBonus": r["loot_bonus_percent"], "cargoBonus": r["cargo_bonus_percent"]} for r in q("select * from authority_levels order by level")],
         "decodedStats": {"static": sum(1 for p in points if p.get("lootStatus") == "static_reference"), "node": sum(1 for p in points if p.get("lootStatus") == "node_reference")},
         "pointLootSource": POINT_LOOT_SOURCE, "hub": hub, "acquisition": acquisition, "acquisitionNotes": ACQUISITION_NOTES,
         "acquisitionAudit": {"itemCount": len(items), "withConfirmedSource": with_source, "withoutConfirmedSource": len(items) - with_source, "conversionRules": len(rule_rows), "resolvedContainers": len(containers), "note": AUDIT_NOTE}}

# ---------- database-only details for item cards
is_broken = lambda n: n in BROKEN_TYPE_NAMES or not re.search("[а-яё]", n, re.I) or n.startswith("item_type_")
db_items = {}
for r in item_rows:
    x = {"type": r["type_native"] if is_broken(r["type_name"]) else r["type_name"], "typeId": r["type_id"], "names": {} if r["game_id"] in WRONG_LOCALIZATION else {c: v["name"] for c, v in sorted(names[r["id"]].items()) if c != "ru"}, "stack": attrs[r["id"]].get("stack-size")}
    if "armor-segments" in attrs[r["id"]] or "armor-blocking-rate" in attrs[r["id"]]:
        x["armor"] = {"segments": attrs[r["id"]].get("armor-segments"), "blockingRaw": attrs[r["id"]].get("armor-blocking-rate")}
    index = attrs[r["id"]].get("sell-price-modifier-index")
    if attrs[r["id"]].get("sell-available") and index is not None:
        x.update(sell=sell_price(attrs[r["id"]]["base-price"], index), sellMultiplier=SELL_MODIFIERS[index])
    db_items[r["game_id"]] = x
broken_types = sorted({(r["type_native"], r["type_name"]) for r in item_rows if is_broken(r["type_name"])})
for r in q("select * from weapon_stats"):
    db_items[r["game_id"]]["weapon"] = {
        "magazine": num(r["magazine_capacity"]), "automatic": r["is_automatic"], "ammo": r["ammo_game_id"],
        "raw": {"maxDamage": num(r["max_damage"]), "maxDamageDistance": num(r["max_damage_distance"]), "headModifier": num(r["head_damage_modifier"]),
                "cooldown": num(r["shot_cooldown_raw"]), "reload": num(r["reload_cast_time_raw"]), "reloadMin": num(r["min_reload_cast_time_raw"]),
                "aimIn": num(r["aiming_in_time_raw"]), "aimOut": num(r["aiming_out_time_raw"]), "takeIn": num(r["take_in_time_raw"])}}
for r in q("select game_id, position, length_raw, damage_raw from weapon_damage_intervals order by 1,2"):
    db_items[r["game_id"]]["weapon"].setdefault("intervals", []).append([num(r["length_raw"]), num(r["damage_raw"])])
for r in q("select i.game_id ammo, t.game_id target from item_compatibility x join items i on i.id=x.item_id join items t on t.id=x.target_item_id join compatibility_types c on c.id=x.compatibility_type_id where c.slug='ammunition-for' order by 2"):
    db_items[r["ammo"]].setdefault("ammoFor", []).append(r["target"])

for r in q("select i.game_id, count(*) types, min(o.f_count) lo, max(o.f_count) hi, max(o.f_take_time) take from cfg_loot_objects o join items i on i.id=o.item_id group by 1"):
    db_items[r["game_id"]]["worldLoot"] = {"types": r["types"], "countMin": num(r["lo"]), "countMax": num(r["hi"]), "takeMs": num(r["take"])}

scene = q("select f_scene, f_category, f_entity_id, f_object_name, f_x x, f_y y, f_z z from cfg_scene_points where point_id is null order by 1,2,3")
hub_rows = [r for r in scene if "hub" in r["f_scene"]]
sector_rows = [r for r in scene if "sectorcenter" in r["f_scene"]]
hub_objects = []
atm = next((r for r in hub_rows if r["f_object_name"] == "CashWithdrawal_ATM"), None)
if atm:
    hub_objects.append({"name": "Банкомат и сейф", "px": round((float(atm["x"]) - HUB["x_min"]) * hub["width"] / (HUB["x_max"] - HUB["x_min"]), 2),
                        "py": round((HUB["z_max"] - float(atm["z"])) * hub["height"] / (HUB["z_max"] - HUB["z_min"]), 2), "entities": [int(r["f_entity_id"]) for r in hub_rows]})
gaps = q("""select (select count(*) from acquisition_sources where drop_probability is not null) drops, (select count(*) from vendor_offers where purchase_price is not null) prices,
  (select count(*) from vendors where location_id is not null) vendor_locations, (select count(*) from verification_issues where resolved_at is null) issues""")[0]
conn.close()
db = {"build": atlas["build"], "source": "supabase:robrun_wiki", "items": db_items, "hubObjects": hub_objects, "unplaced": len(sector_rows)}

# ---------- validation: nothing is written unless all of this holds
errors = []
ids, point_ids = {i["id"] for i in items}, {p["id"] for p in points}
if len(ids) != len(items) or len(point_ids) != len(points):
    errors.append("Повторяются ID предметов или точек")
for i in items:
    if not (DIST / i["icon"]).exists():
        errors.append(f"Нет иконки {i['icon']} для предмета {i['id']}: добавьте файл в dist/assets/items")
    if None in (i["price"], *i["cells"]):
        errors.append(f"У предмета {i['id']} нет цены или размера")
for k, v in acquisition.items():
    if "audit" not in v:
        errors.append(f"Нет аудита источников для {k}")
for p in points:
    if p["px"] is None or p["py"] is None:
        errors.append(f"У точки {p['id']} нет координат карты")
    errors += [f"Точка {p['id']}: неизвестный предмет {e['id']}" for e in p["loot"] if e["id"] not in ids]
for b in buildings:
    if b["px"] is None or not (DIST / b["icon"]).exists():
        errors.append(f"У здания {b['key']} нет координат или иконки")
if errors:
    print("\n".join(errors[:40]))
    sys.exit(f"Сборка остановлена, файлы не изменены: ошибок {len(errors)}")

# ---------- report: what this build changed compared to the previous data.js
def by_key(rows, key="id"):
    return {r[key]: r for r in rows}


prev_path = DIST / "data.js"
prev = None
if prev_path.exists():
    s = prev_path.read_text("utf-8")
    prev = json.loads(s[s.index("{"): s.rindex("}") + 1])
L = ["# Последняя сборка атласа из базы", "", "Создаётся командой `npm run db:build`. База только читается.", "",
     f"- **Сборка игры:** `{atlas['build']}`.",
     f"- **Предметов:** {len(items)}, с подтверждённым источником {with_source}, без источника {len(items) - with_source}.",
     f"- **Точек:** {len(points)}, зданий {len(buildings)}, рецептов Бартера {len(barter)}.", "", "## Изменения относительно предыдущей сборки", ""]
if prev:
    sections = (("Предметы", by_key(prev["items"]), by_key(items)), ("Точки", by_key(prev["points"]), by_key(points)), ("Здания", by_key(prev["buildings"], "key"), by_key(buildings, "key")),
                ("Рецепты Бартера", by_key(prev["barterRecipes"]), by_key(barter)), ("Способы получения", prev["acquisition"], acquisition))
    L += ["| Раздел | Добавлено | Удалено | Изменено |", "|---|---:|---:|---:|"]
    detail = []
    for name, a, b in sections:
        added, removed, changed = sorted(map(str, b.keys() - a.keys())), sorted(map(str, a.keys() - b.keys())), sorted(str(k) for k in a.keys() & b.keys() if a[k] != b[k])
        L.append(f"| {name} | {len(added)} | {len(removed)} | {len(changed)} |")
        for label, values in (("добавлено", added), ("удалено", removed), ("изменено", changed)):
            if values:
                detail.append(f"- **{name}, {label}:** " + ", ".join(f"`{v}`" for v in values[:40]) + (f" и ещё {len(values) - 40}" if len(values) > 40 else ""))
    L += ["", *detail] if detail else []
else:
    L.append("Предыдущей сборки нет.")
L += ["", "## Чего пока нет в базе", "", "- Множителей цены продажи: они заданы в `scripts/build-from-db.py` по данным сборки 26342425.", f"- Вероятностей выпадения заполнено: {gaps['drops']}.", f"- Цен покупки у торговцев заполнено: {gaps['prices']}; расположений торговцев: {gaps['vendor_locations']}.",
      f"- Незакрытых пунктов проверки: {gaps['issues']}.", "", "## Испорченные названия типов", "", "Показано внутреннее имя из игры.", "", "| Внутреннее имя | Строка в базе |", "|---|---|"]
L += [f"| {a} | {b} |" for a, b in broken_types]
L += ["", "## Исправления текстов игры", "", f"- Имя торговца задано вручную: {', '.join(f'`{k}` — {v}' for k, v in VENDOR_NAMES.items())}.",
      "- В описаниях камер `{0}` заменён требуемым уровнем известности.", "- К названиям ключей от сейфов и комнат добавлено место из их описаний.",
      "- Название и описание склада у этих предметов заменены внутренним именем и пояснением: " + ", ".join(f"`{k}`" for k in sorted(WRONG_LOCALIZATION)) + "."]
L += ["", "## Объекты без карты", "", "Сцена SectorCenter: нет карты и проекции, поэтому объекты не показаны.", "", "| Entity | Категория | Объект | X | Y | Z |", "|---:|---|---|---:|---:|---:|"]
L += [f"| {int(r['f_entity_id'])} | {r['f_category']} | {r['f_object_name']} | {float(r['x']):.2f} | {float(r['y']):.2f} | {float(r['z']):.2f} |" for r in sector_rows]

# ---------- write
out_dir.mkdir(parents=True, exist_ok=True)
files = {out_dir / "data.js": "window.ATLAS_DATA=" + json.dumps(atlas, ensure_ascii=False, separators=(",", ":"), default=num) + ";\n",
         out_dir / "db.js": "window.ATLAS_DB=" + json.dumps(db, ensure_ascii=False, separators=(",", ":"), default=num) + ";\n"}
if out_dir == DIST:
    files[REPORT] = "\n".join(L) + "\n"
for path, text in files.items():
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, "utf-8", newline="\n")
    os.replace(tmp, path)
print(f"Собрано из базы: сборка {atlas['build']}, предметов {len(items)}, точек {len(points)}, зданий {len(buildings)} -> {out_dir}")
