import {spawnSync} from 'node:child_process';import fs from 'node:fs';
const python=['.venv/Scripts/python.exe','.venv/bin/python'].find(p=>fs.existsSync(p));if(!python)throw Error('Нет .venv: создайте его и установите research-requirements.txt');
process.exit(spawnSync(python,['scripts/build-from-db.py'],{stdio:'inherit'}).status??1);
