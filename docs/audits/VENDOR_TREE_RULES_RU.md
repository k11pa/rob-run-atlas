# Правила изучения поставок

Проверено 03.11.2026 по установленной сборке 26377677. Изменений БД, сайта или GitHub не выполнялось. Значения ниже — встроенная конфигурация VendorTreeNodesRealmVersion0, а не прочитанное состояние сервера или персонажа. Параметры выбираются через GetVersionConfig(realmVersion).

## Проверка тира

VendorTreeExtensions.CheckTierRequirement получает SelfSector, VendorTreeNodeParams и realmVersion. Фактический тир берётся из SectorDescriptionExtensions.GetParams(SelfSector, realmVersion).Tier. Если RequiredTier отсутствует, условие пройдено. Если RequiredTier задан, а своего сектора/его тира нет, условие не пройдено. Иначе сравниваются индексы: actualTier.Index >= requiredTier.Index. В нативной инструкции используется setge; в CanUnlockClient/TryCanUnlockCommon отказ выполняется при JumpIfLess.

SelfSector читается из RegionUserSettlementModel; тот же getter непосредственно используется в VendorTreeRequirementsViewUpdater.RedrawTierCondition. Это тир сектора/района, связанного с поселением игрока. Проверки уровня здания дома в этом условии нет. Сам getter SelfSector читает реплицируемое значение; точный серверный порядок его назначения при аренде/переселении здесь не восстанавливался.

## Остальные условия

Узел должен быть включён для версии мира и ещё не изучен. Проверяются разрешение роли и режима на изучение, допустимое состояние персонажа; в соответствующем режиме требуется находиться внутри своей базы. Все узлы RequiredNodes должны быть изучены. Проверяются требуемый срок (RequiredImprisonmentYears), монеты CoinsPrice и цена предметами ItemsPrice. Для монет есть дополнительная проверка доступности связанного денежного аккаунта. В UI отдельно существует блокировка изучения во время рейда. Условия необязательно заданы для каждого узла: нулевой порог/пустой список не добавляют требование.

## Подтверждённый пример: мини-бур

| Параметр изучения | Отмычка (lockpick_1) | Мини-бур (mini_drill_1) |
|---|---|---|
| Узел | Lockpick1, index 27 | MiniDrill1, index 29 |
| Включён | Да | Да |
| Наличные cash_1 | 5 000 | 100 000 |
| CoinsPrice | 0 | 0 |
| Требуемый срок | 0 | 0 |
| Требуемый тир | Не задан | Tier2 (index 1) |
| Предыдущие узлы | Пустой список | Lockpick1 |

Путь: изучить поставку «Отмычка» → выполнить требование собственного сектора тира II или выше → заплатить 100 000 наличных за изучение «Мини-бура». Требования к состоянию/месту персонажа остаются применимыми. Это открытие поставки, а не выдача или покупка самого инструмента.

## Доказательство предшественника мини-бура

- В Build() для MiniDrill1 callback списка RequiredNodes берётся из static offset 240 класса VendorTreeNodesRealmVersion0+<>c и передаётся в stack:0x30 перед VendorTreeNodeWithParams.New (ISIL 3308, 3328, 3336, 3342).
- В метаданных этого класса поля идут <>9, <>9__0_0 ... <>9__0_29; 8-байтный static slot 240 соответствует <>9__0_29.
- Callback <Build>b__0_29 создаёт список и добавляет VendorTreeNodeDescriptions static offset 224. Getter get_Lockpick1 читает тот же offset 224 (node index 27).
- Callback <Build>b__0_27 возвращает пустой список.

## Локальные источники

От корня рабочего пространства:

- work/update_audit_26377677/native/IsilDump/Models/Models/Utils/Extensions/VendorTreeExtensions.txt: CheckTierRequirement, TryCanUnlockCommon, CanUnlockClient, CanUnlockServer.
- work/update_audit_26377677/native/IsilDump/Models/Models/References/VendorTree/VendorTreeNodeParams.txt.
- work/update_audit_26377677/native/IsilDump/Models/Models/References/Realm/SectorParams.txt.
- work/update_audit_26377677/native/IsilDump/Models/Models/Models/RegionUserSettlement/RegionUserSettlementModel.txt.
- work/update_audit_26377677/native/IsilDump/Battle/Game/Battle/VendorTree/VendorTreeRequirementsViewUpdater.txt: RedrawTierCondition.
- work/update_audit_26377677/native/IsilDump/Models/Models/ReferencesProject/Descriptions/VendorTree/Versions/VendorTreeNodesRealmVersion0.txt и NestedType___c.txt.
- work/vendor-tree-check/unlocks_native.json: 172 извлечённых набора скалярных требований. Предшественники всех 172 узлов автоматически не восстановлены; два описанных callback проверены отдельно.

Исследовательская копия скрипта work/vendor-tree-check/recover_current.py использует текущие нативные данные и пишет отдельный результат. Игровые файлы только читались. SHA256 GameAssembly.dll: eadb6896d996a41551325d4664ffe07e543629ff7cbbcbab3b8e76a4772f5ea8.
