// Read-only audit of snapshots obtained from the live Supabase SQL Editor.
// This never updates game data, generated atlas files, or the remote database.
import fs from 'node:fs';
const dir = 'docs/audits';
const all = JSON.parse(fs.readFileSync(`${dir}/supabase-all-items-2026-11-03.json`, 'utf8'));
const links = JSON.parse(fs.readFileSync(`${dir}/supabase-acquisition-2026-11-03.json`, 'utf8'));
if (all.project !== links.project) throw Error('Snapshots belong to different projects');
const seen = new Set();
const rows = all.items.map(i => {
  if (seen.has(i.game_id)) throw Error(`Duplicate item: ${i.game_id}`);
  seen.add(i.game_id);
  const methods = (i.methods || []).filter(m => m.method !== 'unknown');
  const advertised = [...new Set(links.links.filter(l => l.game_id === i.game_id && l.link_kind === 'advertised_reward').map(l => l.location))];
  return {...i, hasSource: methods.length > 0, advertisedLocations: advertised,
    probabilityCount: methods.reduce((n, m) => n + m.probabilities, 0)};
});
for (const i of links.unknown) if (!seen.has(i.game_id)) throw Error(`Missing item: ${i.game_id}`);
const unknown = rows.filter(i => !i.hasSource);
const hinted = unknown.filter(i => i.advertisedLocations.length);
const summary = {
  project: all.project, queriedAt: all.queried_at,
  items: rows.length, withSource: rows.length - unknown.length, withoutSource: unknown.length,
  unknownWithBuildingHint: hinted.length, unknownWithoutBuildingHint: unknown.length - hinted.length,
  sourcesWithProbability: rows.reduce((n, i) => n + i.probabilityCount, 0),
  itemsWithAccessIssue: rows.filter(i => i.issues?.includes('complete_access_chain')).length,
};
const esc = s => String(s).replaceAll('|', '\\|').replaceAll('\n', ' ');
const text = [
  '# Аудит способов получения — 03.11.2026', '',
  `Источник: Supabase \`${all.project}\`, схема \`robrun_wiki\`. Запрос: ${all.queried_at}.`, '',
  `Проверены все ${summary.items} предметов. Есть хотя бы один источник у ${summary.withSource}; нет у ${summary.withoutSource}.`,
  `Из неизвестных у ${hinted.length} есть подсказка здания, у ${summary.unknownWithoutBuildingHint} нет и её.`,
  `Заполненных вероятностей: ${summary.sourcesWithProbability}. Незакрытая проверка полной цепочки доступа: ${summary.itemsWithAccessIssue} предметов.`, '',
  'Наличие источника не доказывает полноту цепочки. advertised_reward — подсказка карточки здания, не подтверждённый лутпул. Место применения ключа не является местом его выпадения. spawn_probability — размещение узла, не вероятность предмета.', '',
  '## Все предметы без подтверждённого источника', '',
  '| ID | Предмет | Тип | Подсказки зданий (не лутпул) |',
  '|---|---|---|---|',
  ...unknown.map(i => `| ${esc(i.game_id)} | ${esc(i.name)} | ${esc(i.item_type)} | ${esc(i.advertisedLocations.join(', ') || 'Нет')} |`), '',
  '## Что необходимо для точного заполнения', '',
  'Для случайного дропа нужны: идентификатор пула, привязка к точке/типу контейнера, состав, вероятность или веса вместе с алгоритмом выбора, число попыток и условия (уровень, тир, версия). Один вес не является процентом. Пустые значения нельзя заменять нулём или 100%.', '',
  'Снимки SQL содержат исходные результаты чтения Supabase. Игровые файлы на ПК при этом аудите не читались. Supabase и GitHub не изменялись.', '',
].join('\n');
fs.writeFileSync(`${dir}/ACQUISITION_GAPS_RU.md`, text);
fs.writeFileSync(`${dir}/acquisition-gap-summary.json`, JSON.stringify({summary, items: rows}, null, 2) + '\n');
console.log(JSON.stringify(summary, null, 2));
