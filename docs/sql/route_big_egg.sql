-- Маршрут к BIG EGG #53. Выполняется вручную один раз, затем: npm run db:build
-- Всё в одной транзакции: при ошибке база не изменится. Повторный запуск остановится на уникальных slug.
begin;
set local search_path = robrun_wiki;

insert into source_kinds (slug, name_ru, name_en)
values ('player-observation', 'Наблюдение игрока', 'Player observation');

insert into sources (slug, source_kind_id, description_ru, description_en)
values ('player-big-egg-glass-cutter', (select id from source_kinds where slug = 'player-observation'),
  'Подтверждено владельцем проекта в игре, 2 ноября 2026: стеклорез расходуется, ключ-карта vip_key_6 не нужна',
  'Confirmed in game by the project owner, 2 November 2026: the glass cutter is consumed, key card vip_key_6 is not needed');

insert into acquisition_routes (slug, item_id, title_ru, notes, source_id, evidence_state_id, gate_point_id, scope_note, native_route_id)
values ('egg-faberge-1-gallery-special-exhibit',
  (select id from items where game_id = 'egg_faberge_1'),
  'Экспонат в Арт-галерее',
  'Стеклорез расходуется, поэтому на каждую кражу нужен новый. Ключ-карта хранилища галереи для этого не нужна.',
  (select id from sources where slug = 'player-big-egg-glass-cutter'),
  (select id from evidence_states where slug = 'editorial-inference'),
  (select id from loot_points where entity_id = 807),
  'Item descriptions of glass_cutter_1 and tablet_1_full name the gallery exhibit. Consumption and the absence of a key card requirement are player observations; no requirement field exists in the game data.',
  'gallery_special_exhibit');

insert into route_required_items (slug, route_id, item_id, source_id)
values ('egg-faberge-1-gallery-special-exhibit-glass-cutter-1',
  (select id from acquisition_routes where native_route_id = 'gallery_special_exhibit'),
  (select id from items where game_id = 'glass_cutter_1'),
  (select id from sources where slug = 'ru-strings'));

insert into route_steps (slug, route_id, position, instruction_ru, source_id, evidence_state_id, title_ru)
values
  ('egg-faberge-1-gallery-special-exhibit-step-1',
   (select id from acquisition_routes where native_route_id = 'gallery_special_exhibit'), 1,
   'Стеклорез можно выменять у секретной двери Бартера в хабе за 2 заполненных кодовых планшета. Нажми на стеклорез, чтобы открыть рецепт и способ заполнить планшеты.',
   (select id from sources where slug = 'barter'),
   (select id from evidence_states where slug = 'decoded'),
   'До вылазки: получить стеклорез'),
  ('egg-faberge-1-gallery-special-exhibit-step-2',
   (select id from acquisition_routes where native_route_id = 'gallery_special_exhibit'), 2,
   'Стеклорез позволяет украсть экспонат и при этом расходуется. Ключ-карта хранилища галереи не нужна. Взятие занимает 2 секунды.',
   (select id from sources where slug = 'player-big-egg-glass-cutter'),
   (select id from evidence_states where slug = 'editorial-inference'),
   'В галерее: забрать экспонат');

insert into route_step_items (slug, step_id, item_id)
values ('egg-faberge-1-gallery-special-exhibit-step-1-glass-cutter-1',
  (select id from route_steps where slug = 'egg-faberge-1-gallery-special-exhibit-step-1'),
  (select id from items where game_id = 'glass_cutter_1'));

insert into route_step_points (slug, step_id, point_id)
values ('egg-faberge-1-gallery-special-exhibit-step-2-807',
  (select id from route_steps where slug = 'egg-faberge-1-gallery-special-exhibit-step-2'),
  (select id from loot_points where entity_id = 807));

insert into route_evidence_lines (slug, route_id, position, text_en)
values
  ('egg-faberge-1-gallery-special-exhibit-evidence-1', (select id from acquisition_routes where native_route_id = 'gallery_special_exhibit'), 1,
   'glass_cutter_1 description: allows stealing the exhibit in the gallery'),
  ('egg-faberge-1-gallery-special-exhibit-evidence-2', (select id from acquisition_routes where native_route_id = 'gallery_special_exhibit'), 2,
   'tablet_1_full description: exchange in barter for the glass cutter; recipe glass_cutter_1 takes tablet_1_full x2'),
  ('egg-faberge-1-gallery-special-exhibit-evidence-3', (select id from acquisition_routes where native_route_id = 'gallery_special_exhibit'), 3,
   'Scene Gallery/LootObjectSet_SpecialShowcase/museum_special_showcase_exhibit, entity 807, loot object grand heist index 4'),
  ('egg-faberge-1-gallery-special-exhibit-evidence-4', (select id from acquisition_routes where native_route_id = 'gallery_special_exhibit'), 4,
   'Player observation 2026-11-02: glass cutter consumed, key card vip_key_6 not needed');

commit;
