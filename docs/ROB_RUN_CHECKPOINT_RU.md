# ROB RUN — продолжить с опубликованной версии 6

01.11.2026: версия6 опубликована, status=succeeded, приватный доступ сохранён. Актуальный commit27234abc25a6e654776ed097e710c169c6da5968. IDs: ROB_RUN_Atlas_RELEASE_v6.json.
https://rob-run-loot-atlas.poznergpt.chatgpt.site/#item=deposit_box_1_full

## Основная незавершённая цель

Пользователь просит ВСЕ пути получения всех предметов ОТ и ДО, включая источники ингредиентов и инструментов. Общая цель пока НЕ завершена. Проверены506 предметов:235 имеют хотя бы один подтверждённый источник,271 без восстановленного источника. Даже у235 ещё не все условия доступа/предыдущие узлы торговца известны. Не писать «все пути готовы». Случайные серверные лутпулы по-прежнему не восстановлены.
Человекочитаемый полный506-строчный аудит: outputs/ROB_RUN_ITEM_ACQUISITION_AUDIT_RU.md. Машинный: item-assets/acquisition_audit_all_506.json. Обновлённый граф всех506: item-assets/acquisition_graph.json версии6.

## Исправлена важная ошибка прошлого отчёта

В v5 неверно сказали, что источник vip_key_5 неизвестен. Рецепт УЖЕ присутствовал в decoded_barter и сайте: recipeID vip_key_2, result vip_key_5 за deposit_box_1_full×1. ID рецепта НЕ равен ID результата! Пользователь заметил, что не объяснён источник заполненных ключей. Предыдущие отчёты ниже исторические; этот заголовок их исправляет.

Подтверждённая цепочка:
- deposit_box_1_cumulative (inventory414) — незаполненные ключи, laptop TierIII, отдельный VendorTreeNode30.
- Носить с собой, взламывать bank_cell_1: +1 очко; требуется60 очков. Есть12 точных ячеек1493,1495,..1515. При максимуме результат415=deposit_box_1_full.
- Полные ключи → Бартер хаба → vip_key_5 ID-карта → дверь756 → золотохранилище.
- Большойбур drill_1 остаётся требованием vaultdoor690. Сам бур получается через заполненную экшн-камеру2 + полныйUSB +10000cash.
- Для bank_cell_1 не задан предметный ключ, canBeDrilled=false, стандартный взлом доступен при подходящем состоянии. Не путать накопительные «ключи от ячеек» с физическим ключом для открытия конкретной ячейки. Вход в помещение/сторона vaultdoor для каждой ячейки отдельно не восстановлены, не выводить по соседству.
- Большие bank_safe1487/1489/1491: тип45, hard,canBeDrilled=true,mini_drill_1,drill120сек. Они НЕ являются обязательным шагом заполнения банковских ключей: у bank_safe нет награды cumulativeType0.

## Исследовательский прорыв: все208 контейнеров

Cpp2IL длина BuildContainers11828 обрезалась на первом return, хотя настоящий диапазон до следующего native-метода106928байт. work/map-assets/config-decode/recover_full_containers.py линейно разбирает полный диапазон черезcapstone, отслеживает явные константы, enumgetters и вызовы LocationContainerDescription.New.
Полностью восстановлены208 уникальных контейнеров с индексами0..207. Все EntityID совпали с городской сценой (исключить hub entity4!). Все17 старых ISILtuple контейнер/тип/ключ независимо совпали.
Данные map-assets/native-loot/FullContainers.json, validation содержит проверки. Каждый контейнер сайта теперь имеет containerTypeId/index, requiredItems, drillAllowed, drillTimeMs, cumulativeRewards.
Стек New проверен: containerDescription stack0x20, requirementItem stack0x40. Поле description в старом VM было r9=inventoryEntityId, для контейнерного типа использовать raw_stack0x20 либо новыеFullContainers.

## Все9 накопительных конверсий

work/item-assets/decode_cumulative.py восстановил9CumulativeItemDescription +6типов +2ChargerDescription из публичногоreferences.dat, последовательныеиндексы.
depositkeys60;USB5;tablet4;cargo_manifest1/2/3=5/12/36;camera1/2/3=40/70/100, authorityindices1/2/3 означают уровни2/3/4. RequiresAuthority уtype4=true; не писать ≥ без проверки (описание «при {0}-м уровне»).
Исходные inventoryrefs CumulativeItemDescriptionFunc однозначно связывают9 незаполненных предметов с конверсией; resultitemref даётполныйвариант. Тип0depositkeys,1USB,2tablet,3manifest,4camera,5lab_flask.
ContainerDescription.cumulative_points — начисление накопительномутипу; НЕ предметные требования к открытию! Тип0 у12bank_cell_1, тип2 у60контейнеров, тип4 у208контейнеров.
ИсточникиUSB:16компьютеров2698..2713, CumulativeChargerDescription0/1 даёт1/2очка. Все16 nativeEntityID сравнились с registryLocationCumulativeChargerViews. Полная матрица сцены и точныепозиции сохранены map-assets/verified_computer_sources.json, native-loot/ComputerChargers.json. work/add_computer_sources.py воспроизводит.
Условия доступа в конкретную запертуюкомнату компьютера пока НЕ связаны с конкретнымключом. Это явно показано, не назначать ключтолько по близости.

## Открытия торговца и интерфейс

work/item-assets/recover_vendor_unlocks.py восстановил168 базовыхnative VendorTreeNodesRealmVersion0: itemcostсписки,coins,requiredYears,tier. Данные native_vendor_unlocks_WIP.json; названиеWIP сохранено, поскольку предыдущиеузлы и текущаяrealmверсия не проверены. ВUI показываются только resolveditemcost с предупреждением «базовые параметры, предыдущиеузлы/настройкимира не проверены».
Для ключейnode30nativeстоимость открытия100000cash,miniDrillnode29=100000cash,lockpicknode27=5000cash. Это открытиеузла, НЕ окончательнаяцена покупки. Не выводить покупнуюцену из BasePrice безформулы.

Во всех506 карточках теперь единая рекурсивная система acquisitionTree:
- все известныепокупки;
- каждый рецептБартера со всемиингредиентами, раскрывающими собственныеисточники;
- заполнение полноговарианта через покупкупустого, цельвочках, условияизвестности, конкретныеточкиначисления;
- списоккартолокаций для точноизвестногофиксированноголута;
- защитаотциклов и глубина6, дальше ссылка в карточку (не «полныйпуть»приобрыве).
Карточкипустыхнакопителей показывают, какполучитьполныйрезультат. Вкарточкахконтейнеров способывскрытия и начисленияпредметам. Вкарточкахключей/минибура ссылкинаконтейнеры.
Вкаталогедобавленфильтр «найденисточник/не найден/заполнение». ВОданных235/271статистика. Всего926точек=890лут+20дверей+16компьютеров; прогрессобхода890, действия/дверинеобнуляютмаксимум. Исправленhashпереходitem→point, чтобы закрыватьмодалки.

## Воспроизведение и проверки

Стабильныеv3/v4/v5основыне пересобирать безнужды. Послеenrich_acquisition.py→build_access_routes.py выполнитьwork/enrich_all_acquisition.py→work/add_computer_sources.py. Первыйновыйскрипт обновляетграфи208контейнеров; второйобязателендля16USBточек (иначеUSBactionPoints0). Идемпотентностьпроверятьскриптами, UIмиграцииодноразовые.
work/update_dependency_ui.py и work/finalize_dependency_ui.py УЖЕприменены, не запускать повторно. Актуальныйупаковщикwork/save_full_chain_checkpoint.py; старыеупаковщикиперезапишутreleaseстарымиv3/v4/v5.
node --checkapp/data пройдены;926uniqueIDs,208точныхjoin,9конверсий,всеitem/pointrefs проверены. Браузер:полныеключи→покупкапустого→ценаоткрытия100000cash→источникиcash;12ячеек+1;USB5очков16компов;компьютер2698+1;hashзакрытиемодалки. Сохранёнскрин ROB_RUN_Full_keys_chain_preview.png. Deploymentv6status=succeeded.
Офлайнсайт, sourcecheckpoint и исследовательскийархив обновлены. Секретов/учётныхданныхнет. public-config.jsonпо-прежнемуНЕпубликовать.

---
История предыдущих контрольных точек:

# ROB RUN — продолжить с опубликованной версии 5

01.11.2026: опубликована версия5, Sites status=succeeded, доступ owner-private сохранён. Точные IDs: ROB_RUN_Atlas_RELEASE_v5.json. Commit 4c5da5bcc8e0a086c25c2edf4ce63c10ec0bc861.
https://rob-run-loot-atlas.poznergpt.chatgpt.site/#item=gold_bar_1

## Новая задача пользователя и результат

Пользователь хочет для каждого предмета цепочку необходимых инструментов/ключей. Для обычного лута — простое описание магазина/дома без лишней цепочки, но отсутствие требований нельзя выводить из редкости. Начали с золотого слитка.

В карточке gold_bar_1 теперь маршрут с кликабельным списком «Что понадобится» и нумерованными шагами:
1. Получить большой легендарный drill_1 (Бартер в хабе; рецепт остаётся кликабельным).
2. Открыть дверь банковского хранилища690. Установка5с, unlockTime60000мс.
3. Внутренняя дверь756 требует vip_key_5 — экзотическая ID-карта. Её описание прямо говорит «Открывает золотохранилище в банке». Источник самой карты НЕ найден и честно помечен неизвестным.
4. Забрать золото с7 узлов313..319: каждый isLocked=false, 1 слиток за действие, 9 действий. Мини-бур для сбора этих узлов не требуется.
Ещё один отдельный слиток811 есть в банке, но его нахождение за внутренней дверью756 НЕ подтверждено, поэтому для него не заявлено обязательное наличие ID-карты. Золото не описывается как исключительно случайный дроп малых сейфов.

Связь BankGold узлов с золотохранилищем следует из назначения ID-карты и расположения объектов в сцене, а не из поля gate на каждом узле (такого поля в этих описаниях нет). Нельзя превращать это в универсальный алгоритм «весь лут здания за каждой дверью».

Добавлена категория «Двери и доступ»:20 объектов, 19 с ключами + vaultdoor690. Все присоединены к сцене точно по EntityID и registry _ids/_views, координаты рассчитаны полной матрицей родительских трансформов. Карточки дверей показывают предмет для открытия, карточки ключей — двери, которые они открывают. Всего910 точек карты; исходные890 lootpoints сохранены. Двери не входят в прогресс обыска (знаменатель890).
Обычные карточки с известными точками получили краткое «Можно добыть при ограблении: ...». Отсутствие инструмента для самого сбора указывается лишь для static world item и node.isLocked=false, отдельно от условий входа. Не утверждать, что у всех серых/синих предметов вход свободен или что известны все случайные пулы.

## Новые доказательства и декодеры

- item-assets/decoded_container_requirements.json:47 типов ContainerDescription и4 типа ContainerDrillDescription, последовательные индексы. bank_safe индекс45 → drill_index3/hard, canBeDrilled=true, drillTime120000мс. bank_cell_1/2 → drill none/canBeDrilled=false. Не объявлять всем малым сейфам обязательный мини-бур: он альтернативный механизм там, где разрешено; ключи и unlockstate нужно проверять отдельно.
- item-assets/decoded_vault_config.json: найдено уникальное совпадение битовой последовательности публичного references.dat с UnlockSafeDoorConfig: requiredPlayersCount12,setDrill5000,removeDrill4000,reward3500,inventoryref239=drill_1. RequiredPlayersCount12 НЕ равно доказанному требованию12 человек в группе, значение в UI не показано. Native CheckSet проверяет состояние мира/кинематического контроллера; нужно отдельно расшифровать смысл этого порога.
- map-assets/verified_access_points.json:20 точных объектов доступа и полный маршрут золота с evidence/scope.
- work/item-assets/decode_container_requirements.py: schema ID,index,typeRef,drillRef,unlockTime64,nullableDict(cumulativeTypeRef→points32). Поле cumulative_points НЕ помечать требованиями открытия: вероятно очки накопительных предметов за обыск, смысл отдельно проверить!
- work/item-assets/find_vault_config.py: уникальный поиск constantbits и чтение настоящего публичного конфига, с проверкой itemref239.
- work/build_access_routes.py: воспроизводимая сборка accesspoints+nodeLocked+goldroute; идемпотентен.
- work/update_route_ui.py: одноразовая миграция уже применена. НЕ запускать повторно; есть assert-защита.
- work/inspect_bank.py: первая разведка по полям entity дала0, поскольку IDs хранятся в registry, а не в MonoBehaviour; пустой work/bank_entities.json не считать отсутствием объектов. Использовать исправленный registryподход в build_access_routes.py.

Нативные доказательства:
References/Safe/UnlockSafeDoorConfig.txt и serializer;
ReferencesProject/Descriptions/Safe/UnlockSafeDoorConfigs_NestedType___c.txt: itemstaticoffset1920 → index239 drill_1;
References/Container/UnlockDescription.txt get_DrillItem: staticoffset1928 → index240 mini_drill_1;
References/Location/LocationContext/Generated/CityLocationContextBuilder.txt ISIL55163: SafeDoorDescription.New entity690,unlock60000;
References/Door/LocationDoorDescription.New signature: requirement8tharg=stack0x38, подтверждена;
Scene registry MonoBehaviour343911: LocationSafeDoorViews690→354478→Bank/Editor_VaultDoor_01; Door756→Bank/DoorSingleGrid_02.

## Проверка и продолжение

node --check app.js/data.js; проверены910 уникальных EntityID/конечных координат,20 requiredItemrefs и все ссылки маршрута. В браузере проверены gold route, обе карточки предметов, переход к двери756 и её требуемый ключ. Скриншот ROB_RUN_Gold_route_preview.png сохранён после повторной отрисовки (первый screenshot сразу после scroll был пустым из-за ещё не завершённого кадра).
Полные вероятности контейнеров/случайныхточек, источник vip_key_5 и всех других ключей пока не найдены. Следующие шаги: источник ID-карты; item→конкретныйконтейнер→дверь для остальных ценных предметов; дополнительные ключи/условия у банковских ячеек; параметры открытия/прокачки mini_drill_1.

Пайплайн теперь v3 базовые3скрипта → enrich_acquisition.py → build_access_routes.py. enrich_acquisition.py пересоздаёт граф и удалит routes/usedForDoors, поэтому ПОСЛЕ него всегда запускать build_access_routes.py. Базовый finalize_atlas_data.py всё ещё assert890; он рассчитан на этап до добавления дверей. Не запускать весь базовый pipeline без необходимости. Две UIмиграции уже применены — редактировать текущий app.js напрямую.
Не запускать старые save_acquisition_checkpoint.py/package_atlas_release.py: они содержат v4/v3 и перепишут release/checkpoint. Актуальный упаковщик work/save_route_checkpoint.py. Секреты не сохранялись, public-config.json не включать в архивы.

---
История предыдущих этапов:

# ROB RUN — продолжить с версии 4

Версия 4 успешно опубликована 01.11.2026. Доступ приватный, аудитория не изменена.
https://rob-run-loot-atlas.poznergpt.chatgpt.site
Commit ca50e89c5bd337bb6f1e75f6f4614e50225377e9. Точные IDs публикации: ROB_RUN_Atlas_RELEASE_v4.json.

## Новое: способы получения предмета

Пользователь хочет цепочки: предмет → конкретный контейнер/магазин → дверь/ключ → инструмент → где купить/открыть инструмент. Пример — легендарный super_bolt_cutter. Пользователь подтвердил Бартер в хабе. Завтра продолжить отсюда, не повторять извлечения карт и иконок.

В data.js добавлен acquisition-граф для всех 506 предметов: 266 записей покупки для 201 уникального предмета, 11 рецептов с 10 уникальными результатами, обратные ссылки ингредиентов и ссылки на 267 точных точек (21 уникальный тип предмета).
Карточка показывает «Как получить»: ассортимент и тир, рецепты с кликабельными ингредиентами, кнопку возврата по цепочке, точные точки с переходом к карте, отдельные неподтверждённые подсказки наград игровой карты. Добавлены прямые ссылки #item=ID и копирование ссылки.

Проверенные примеры:
- super_bolt_cutter (легендарный): laptop, Tier III. Отдельного VendorTreeNode для него не найдено; не выдумывать обязательный узел прокачки.
- bolt_cutter (зелёный): laptop, Tier II.
- mini_drill_1: laptop, Tier II, есть отдельный VendorTreeNodeDescription index29 → inventory index240. Стоимость открытия, предшествующие узлы и параметры прокачки пока НЕ восстановлены.
- drill_1: Бартер в хабе за action_camera_2_full×1 + usb_1_full×1 + cash_1×10000 (точные ID смотреть в data.js/decoded_barter.json).
- dp9_m2: точный статический лут в стрип-клубе, point802.

Тир — именно Realm.TierDescription, не уровень бандита и не доказанный уровень торговца. Расшифрованы tier_1/2/3, индексы0/1/2. Stock dictionary ключи — ссылки в этот enum. Финальная цена покупки не вычислялась по BasePrice: формулу не проверили.

## Новые исследовательские файлы

- item-assets/decoded_acquisition.json: 3 тира, 168 VendorTreeNodeDescription, индексы и itemref, позиции бинарного потока.
- item-assets/acquisition_graph.json: полный граф получения, источники и сводка.
- map-assets/native-loot/access_requirements_WIP.json: 85 восстановленных записей дверей (19 с прямым ключом), 17 контейнеров (один с safe_key_7), 2 accessentity. Это WIP, в интерфейс НЕ добавлено. Не объявлять полнотой: generated ISIL обрывается в некоторых CFG.
- work/item-assets/decode_acquisition.py: воспроизводит enumтипы и vendorузлы из work/references.dat.
- work/map-assets/config-decode/extract_access_native.py: расширение pureVM из extract_city_native.py, читает Door/Access referencegetter. Для двери requirement stack0x38; для контейнера stack0x40. Контейнерную сигнатуру New и обоих wrapperов независимо проверить перед включением в UI. Исходный ctor LocationContainerDescription имеет inventoryEntityId в r9, контейнерный тип передаётся stack0x20, position stack0x28, orientation stack0x30, interactPoint stack0x38, requirement stack0x40.

Двери с ключами (entity → item):
700 vip_key_3;708 room_key_7;714 vip_key_1;716 room_key_11;722 room_key_2;723 room_key_1;725 room_key_9;733 room_key_12;737 room_key_13;742 vip_key_2;743 vip_key_4;755 vip_key_6;756 vip_key_5;761 room_key_10;764 room_key_5;767 room_key_6;769 room_key_8;783 room_key_3;784 room_key_4.
Контейнер1263 → safe_key_7. Координаты этих объектов ещё не присоединены к карте. Нужна связь по EntityID сцены; соседство не подтверждает «сейф за этой дверью».

## Следующие шаги

1. Присоединить 19 дверей с ключами к сцене по EntityID, проверить координаты и здания, добавить слой дверей. До проверки не связывать сейфы с дверями по расстоянию.
2. Извлечь VendorTreeNodeParams / VendorTreeNodesRealmVersion0: isEnabled, ItemsPrice, CoinsPrice, RequiredImprisonmentYears, RequiredTier, RequiredNodes. Основная Build большая, closure-файл содержит <Build>b__0_0..; параметры зависят от realmversion. Не смешивать дефолтный нативный билд с актуальным config без отметки источника.
3. Проверить CumulativeItemDescription/mini_drill upgrade и ContainerDescription/ContainerDrillDescription, разделить инструмент открытия и потребление ключа.
4. Продолжить поиск серверных случайных lootpool/весов. Пока они не восстановлены. Ассортимент торговца — не пул выпадения магазина; advertised rewards — не таблица контейнера.

## Проверка и воспроизведение

node --check app.js/data.js пройдены. Все506 itemrefs, ссылки рецептов и точек acquisition разрешены. В браузере проверены: #item=super_bolt_cutter; drill_1 → экшн-камера → возврат; dp9_m2 → point802 и карта; исходные функции v3 сохранены. Новую публикацию подтвердил Sites status=succeeded.

Базовый пайплайн v3: prepare_atlas_v3.py → bind_atlas_loot.py → finalize_atlas_data.py, затем обязательно work/enrich_acquisition.py. Последний идемпотентно добавляет граф. work/update_acquisition_ui.py — одноразовая миграция уже применена, повторно НЕ запускать: повторит CSS/обработчики.
work/package_atlas_release.py всё ещё hardcoded v3: НЕ запускать без правки, иначе перезапишет checkpoint старым состоянием. Для v4 использовать work/save_acquisition_checkpoint.py. Исходники и sourcehelper workflow — как ниже в предыдущем checkpoint.

Офлайн-сайт и исследовательский архив обновлены до v4. Никакие креды не сохранены. work/public-config.json содержит посторонние сервисные поля, НЕ печатать и НЕ включать в архивы. Исходные файлы игры не изменялись.

---
Предыдущая контрольная точка версии3 (история и базовые пути):

# ROB RUN — актуальная контрольная точка

Работа сохранена 1 ноября 2026. Версия 3 УСПЕШНО ОПУБЛИКОВАНА.

URL: https://rob-run-loot-atlas.poznergpt.chatgpt.site
Project ID: appgprj_6ae6d56d239481918147cc9c7ec07bb2
Version ID: appgprj_6ae6d56d239481918147cc9c7ec07bb2~appgver_8db75ca633288191b556fa2e5b0a9203
Deployment ID: appgdep_6ae6e5e2d8dc8191a80c57d6ec8dfde5
Commit: 1e09fdbd32cbf122f08ba5ad6d4ff0e89dafa3c8

Исходники: C:/Users/low_low/Documents/Codex/2026-11-01/new-chat/work/rob-run-atlas
Hosting manifest: .openai/hosting.json, static.directory=dist.
Не создавать новый сайт. Сохранить текущий приватный доступ.

## Сделано

Чистая городская карта из исходной геометрии, 506 иконок с реальной редкостью/базовой ценой, 28 официальных карточек зданий, 267 точных привязок предметов (27 статических + все 240 узлов внутри зданий), отдельный план хаба с дверью Бартера Entity15 и 11 рецептами. Пользователь прямо подтвердил, что Бартер находится В ХАБЕ. Поиск, фильтры, категории, отметки обыска и прямые ссылки сохранены.

Структурная проверка: все 506 иконок существуют; все ссылки предметов и рецептов разрешены; 28 имён зданий уникальны; 890 координат конечны. Независимо проверены все 240 нативных ссылок узлов и 27 статических. JavaScript прошёл node --check. В браузере проверены каталог/редкость, узел оружейных деталей 231, красный экспонат в галерее, прямые ссылки и переходы город↔хаб, поиск рецепта по слову «слиток», широкий и мобильный вид.

## Что ещё можно исследовать

Полные пулы и веса случайного лута контейнеров и 330 открытых случайных точек не восстановлены. Не подменять их примерами наград карты или инвентарями торговцев. 53 уличных мусорки 1126–1178 не привязаны к таблицам; все 240 узлов зданий уже покрыты. Городские этажи не размечены. Полный серверный пул не доказывать по названию магазина.

## Данные

- outputs/rob-run-research/item-assets/: decoded_inventory_items.json (506), decoded_loot_objects.json (224), decoded_node_descriptions.json (70), decoded_node_loot.json (61), decoded_barter.json (11 рецептов, 2 торговца), decoded_authority_levels.json, decoded_trader_inventories.json, verified_city_node_joins.json, verified_city_static_joins.json, rarity_palette.json, все иконки.
- outputs/rob-run-research/map-assets/: городские PNG/SVG/геометрия/проекция; building-icons/index.json (28 карточек, 110 примеров наград); native-loot/BuildLootNodes.json и BuildLootObjects.json; hub/ с планом хаба, координатами и README.
- outputs/rob-run-research/point_loot_bindings.json — 267 точных связей.
- work/item-assets/CHECKPOINT.md и work/map-assets/CHECKPOINT.md — подробные исследовательские состояния, скрипты и схемы.
- work/il2cpp-isil/IsilDump/ — статический нативный disassembly/ISIL. В некоторых огромных generated-методах вывод обрывается; для оставшихся уличных точек нужен анализ продолжений CFG.
- work/references.dat — публичный бинарный справочник, SHA256 281754339c0ec25be744e136782d89d05dcda7db0b7b2115b39dfd6d8f533c4f.

## Воспроизведение и важные ограничения

Python: C:/Users/low_low/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe; зависимости work/pydeps.
Данные сайта собираются последовательно: work/prepare_atlas_v3.py → work/bind_atlas_loot.py → work/finalize_atlas_data.py. Первый скрипт сбрасывает p.loot, поэтому обязательно выполнить все три. Не перезаписывать готовый data.js одним первым скриптом.

Для следующего изменения прочитать Sites SKILL.md, get_site, получить новый create_source_repository_write_credential и открыть существующий checkout через site-workflow.mjs. Токены доступа истекают; хранить только в памяти и передавать в stdin. При публикации использовать точный результат helper и owner-private операцию.

work/public-config.json содержит посторонние сервисные поля. НЕ печатать целиком, НЕ включать в архивы и НЕ публиковать. Учётные данные пользователя не использовались. Игра, процессы и античит не изменялись.

Актуальные источники и результаты уже на диске. При возобновлении не повторять завершённые извлечения и не восстанавливать проект заново.
