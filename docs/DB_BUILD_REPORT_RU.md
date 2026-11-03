# Последняя сборка атласа из базы

Создаётся командой `npm run db:build`. База только читается.

- **Сборка игры:** `26342425`.
- **Предметов:** 506, с подтверждённым источником 235, без источника 271.
- **Точек:** 926, зданий 28, рецептов Бартера 11.

## Изменения относительно предыдущей сборки

| Раздел | Добавлено | Удалено | Изменено |
|---|---:|---:|---:|
| Предметы | 0 | 0 | 0 |
| Точки | 0 | 0 | 0 |
| Здания | 0 | 0 | 0 |
| Рецепты Бартера | 0 | 0 | 0 |
| Способы получения | 0 | 0 | 0 |

## Чего пока нет в базе

- Множителей цены продажи: они заданы в `scripts/build-from-db.py` по данным сборки 26342425.
- Вероятностей выпадения заполнено: 0.
- Цен покупки у торговцев заполнено: 0; расположений торговцев: 0.
- Незакрытых пунктов проверки: 1255.

## Испорченные названия типов

Показано внутреннее имя из игры.

| Внутреннее имя | Строка в базе |
|---|---|
| BillOfSale | д |
| BoltCutter | Локализация не найдена |
| CargoChargeWorkbenchUpgrade | item_type_cargo_charge_workbench_upgrade |
| CargoProductionWorkbenchUpgrade | Деревянная статуэтка |
| Consumable | item_type_consumable_RU |
| CryptoWorkbenchUpgrade | CryptoWorkbenchUpgrade |
| PlotBuildingSpecialModule | item_type_plot_building_special_module |
| RouletteChip | Касса |
| VideoCard | VideoCard |

## Исправления текстов игры

- Имя торговца задано вручную: `city_trader_car_parts` — Торговец автозапчастями.
- В описаниях камер `{0}` заменён требуемым уровнем известности.
- К названиям ключей от сейфов и комнат добавлено место из их описаний.
- Название и описание склада у этих предметов заменены внутренним именем и пояснением: `broken_video_card`, `crypto_farm_1`, `crypto_wallet`, `crypto_workbench_1`, `crypto_workbench_cooling_upgrade`, `crypto_workbench_speedup_upgrade`, `video_card_1`.

## Объекты без карты

Сцена SectorCenter: нет карты и проекции, поэтому объекты не показаны.

| Entity | Категория | Объект | X | Y | Z |
|---:|---|---|---:|---:|---:|
| 309 | LocationCashLootNode | TraderMoneyPacks | 60.19 | 9.88 | -16.41 |
| 31 | LocationLootableTargetObjects | LocationRandomLootLevelEditor TrashForCitizen[3] | 61.16 | 9.93 | 40.92 |
| 32 | LocationLootableTargetObjects | LocationRandomLootLevelEditor TrashForCitizen[3] | 46.23 | 9.94 | 53.03 |
| 33 | LocationLootableTargetObjects | LocationRandomLootLevelEditor TrashForCitizen[3] | 72.54 | 12.99 | -24.18 |
| 34 | LocationLootableTargetObjects | LocationRandomLootLevelEditor TrashForCitizen[3] | -7.94 | 10.02 | 3.38 |
| 35 | LocationLootableTargetObjects | LocationRandomLootLevelEditor TrashForCitizen[3] | -5.55 | 10.14 | 0.38 |
| 36 | LocationLootableTargetObjects | LocationRandomLootLevelEditor TrashForCitizen[3] | 66.34 | 9.89 | -32.30 |
| 29 | LocationLootNodes | LootNode_TrashCanBig_01 | -8.25 | 9.01 | 0.52 |
| 30 | LocationLootNodes | LootNode_TrashCanBig_01 | 107.72 | 8.79 | -14.95 |
