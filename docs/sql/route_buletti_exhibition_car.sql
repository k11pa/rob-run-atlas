-- Угон выставочного автомобиля в Гранд-отеле → Buletti Soltempra.
-- Выполняется вручную один раз в схеме robrun_wiki (SQL editor Supabase), затем: npm run db:build
-- Всё в одной транзакции: при ошибке база не изменится. Существующие строки не меняются и не удаляются;
-- повторный запуск ничего не дублирует (on conflict (slug) do nothing).
--
-- Доказательства: локальные файлы установленной сборки 26377677 (см. docs/audits/GRAND_HOTEL_BULETTI_RU.md).
-- Полный маршрут на действующем сервере не проверен. Источник джеммера (auto_flipper_1) не установлен —
-- здесь он НЕ добавляется: ни покупки, ни бартера, ни дропа.
begin;
set local search_path = robrun_wiki;

insert into source_kinds (slug, name_ru, name_en)
values ('game-files', 'Файлы установленной игры', 'Installed game files')
on conflict (slug) do nothing;

insert into sources (slug, source_kind_id, description_ru, description_en)
values ('game-files-26377677-buletti', (select id from source_kinds where slug = 'game-files'),
  'Сборка 26377677, 03.11.2026: AccessEntityDescriptions.Buletti (accessItem = Джеммер auto_flipper_1, castTime 3000, accessGettingDuration 60000, accessResetDuration 3000, accessResetCopSalaryReward 5000), LootObjectItemDescriptions.Buletti (1 × buletti_soltempra, takeTime 2000), GetAccessModel.HandelRequest (предмет ищется в инвентаре), локализация 524788041169735680 и 530184765817745408. Прохождение на сервере не проверено.',
  'Build 26377677, 2026-11-03: AccessEntityDescriptions.Buletti (accessItem = Jammer auto_flipper_1, castTime 3000, accessGettingDuration 60000, accessResetDuration 3000, accessResetCopSalaryReward 5000), LootObjectItemDescriptions.Buletti (1 x buletti_soltempra, takeTime 2000), GetAccessModel.HandelRequest (item searched in inventory), localization keys 524788041169735680 and 530184765817745408. Not verified on a live server.')
on conflict (slug) do nothing;

insert into acquisition_routes (slug, item_id, title_ru, notes, source_id, evidence_state_id, gate_point_id, scope_note, native_route_id)
values ('buletti-soltempra-grand-hotel-exhibition-car',
  (select id from items where game_id = 'buletti_soltempra'),
  'Угон выставочного автомобиля',
  null,
  (select id from sources where slug = 'game-files-26377677-buletti'),
  (select id from evidence_states where slug = 'decoded'),
  (select id from loot_points where entity_id = 795),
  'Access entity 1683 uses AccessEntityDescriptions.Buletti (accessItem auto_flipper_1); loot object buletti gives one buletti_soltempra item. Timers are in ms by the convention of these fields. Unknown: jammer source, whether it is consumed, floor/route inside the hotel, event cooldown, how the item becomes a driveable car. Entity 1684 is the Faberge egg console and is not part of this route.',
  'grand_hotel_exhibition_car')
on conflict (slug) do nothing;

insert into route_required_items (slug, route_id, item_id, source_id)
values ('buletti-soltempra-grand-hotel-exhibition-car-auto-flipper-1',
  (select id from acquisition_routes where native_route_id = 'grand_hotel_exhibition_car'),
  (select id from items where game_id = 'auto_flipper_1'),
  (select id from sources where slug = 'game-files-26377677-buletti'))
on conflict (slug) do nothing;

insert into route_steps (slug, route_id, position, instruction_ru, source_id, evidence_state_id, title_ru)
values
  ('buletti-soltempra-grand-hotel-exhibition-car-step-1',
   (select id from acquisition_routes where native_route_id = 'grand_hotel_exhibition_car'), 1,
   'Найдите консоль выставочного автомобиля в Гранд-отеле. Джеммер должен быть в инвентаре.',
   (select id from sources where slug = 'game-files-26377677-buletti'),
   (select id from evidence_states where slug = 'decoded'),
   'Найти консоль автомобиля'),
  ('buletti-soltempra-grand-hotel-exhibition-car-step-2',
   (select id from acquisition_routes where native_route_id = 'grand_hotel_exhibition_car'), 2,
   'Установите джеммер — 3 секунды.',
   (select id from sources where slug = 'game-files-26377677-buletti'),
   (select id from evidence_states where slug = 'decoded'),
   'Установить джеммер'),
  ('buletti-soltempra-grand-hotel-exhibition-car-step-3',
   (select id from acquisition_routes where native_route_id = 'grand_hotel_exhibition_car'), 3,
   'Дождитесь завершения взлома — 60 секунд. Полиция может прервать взлом.',
   (select id from sources where slug = 'game-files-26377677-buletti'),
   (select id from evidence_states where slug = 'decoded'),
   'Дождаться взлома'),
  ('buletti-soltempra-grand-hotel-exhibition-car-step-4',
   (select id from acquisition_routes where native_route_id = 'grand_hotel_exhibition_car'), 4,
   'После получения доступа заберите Buletti Soltempra — 2 секунды взаимодействия.',
   (select id from sources where slug = 'game-files-26377677-buletti'),
   (select id from evidence_states where slug = 'decoded'),
   'Забрать Buletti Soltempra')
on conflict (slug) do nothing;

insert into route_step_items (slug, step_id, item_id)
values ('buletti-soltempra-grand-hotel-exhibition-car-step-2-auto-flipper-1',
  (select id from route_steps where slug = 'buletti-soltempra-grand-hotel-exhibition-car-step-2'),
  (select id from items where game_id = 'auto_flipper_1'))
on conflict (slug) do nothing;

insert into route_step_points (slug, step_id, point_id)
values ('buletti-soltempra-grand-hotel-exhibition-car-step-4-795',
  (select id from route_steps where slug = 'buletti-soltempra-grand-hotel-exhibition-car-step-4'),
  (select id from loot_points where entity_id = 795))
on conflict (slug) do nothing;

insert into route_evidence_lines (slug, route_id, position, text_en)
values
  ('buletti-soltempra-grand-hotel-exhibition-car-evidence-1', (select id from acquisition_routes where native_route_id = 'grand_hotel_exhibition_car'), 1,
   'Localization 524788041169735680: "Steal the exhibition car from the Grand Hotel"'),
  ('buletti-soltempra-grand-hotel-exhibition-car-evidence-2', (select id from acquisition_routes where native_route_id = 'grand_hotel_exhibition_car'), 2,
   'AccessEntityDescriptions.Buletti: accessItem = InventoryItemDescriptions.AutoFlipper1 (offset 3504); castTime 3000, accessGettingDuration 60000, accessResetDuration 3000, accessResetCopSalaryReward 5000'),
  ('buletti-soltempra-grand-hotel-exhibition-car-evidence-3', (select id from acquisition_routes where native_route_id = 'grand_hotel_exhibition_car'), 3,
   'LootObjectItemDescriptions.Buletti: 1 x buletti_soltempra (InventoryItemDescriptions.BulettiSoltempra, offset 2696), takeTime 2000; scene GrandHotel/Loot/LootObjectSet/buletti, entity 795'),
  ('buletti-soltempra-grand-hotel-exhibition-car-evidence-4', (select id from acquisition_routes where native_route_id = 'grand_hotel_exhibition_car'), 4,
   'GetAccessModel.HandelRequest: InventorySearchRules.FindItem, the jammer must be in the inventory'),
  ('buletti-soltempra-grand-hotel-exhibition-car-evidence-5', (select id from acquisition_routes where native_route_id = 'grand_hotel_exhibition_car'), 5,
   'Localization 530184765817745408: the whole city learns about hacking the museum exhibit or the Grand Hotel console; events buletti_soltempra_attempt / buletti_soltempra')
on conflict (slug) do nothing;

commit;
