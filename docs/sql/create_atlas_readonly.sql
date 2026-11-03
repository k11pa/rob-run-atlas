-- Логин только для чтения, которым npm run db:build собирает атлас.
-- Выполнить один раз в Supabase → SQL Editor. Пароль заменить своим.

create role atlas_readonly with login password 'ЗАМЕНИТЕ_НА_ДЛИННЫЙ_ПАРОЛЬ'
  nosuperuser nocreatedb nocreaterole noinherit noreplication nobypassrls
  connection limit 5;

-- Даже по ошибке не сможет ничего записать, а долгий запрос оборвётся
alter role atlas_readonly set default_transaction_read_only = on;
alter role atlas_readonly set statement_timeout = '60s';
alter role atlas_readonly set search_path = robrun_wiki;

-- Чтение схемы атласа, больше ничего
grant usage on schema robrun_wiki to atlas_readonly;
grant select on all tables in schema robrun_wiki to atlas_readonly;

-- Новые таблицы и представления robrun_owner тоже будут доступны для чтения
alter default privileges for role robrun_owner in schema robrun_wiki
  grant select on tables to atlas_readonly;

-- Проверка: ожидается true, false, false
select has_schema_privilege('atlas_readonly', 'robrun_wiki', 'usage') as can_use_schema,
       has_table_privilege('atlas_readonly', 'robrun_wiki.items', 'insert') as can_insert,
       has_schema_privilege('atlas_readonly', 'public', 'create') as can_create_in_public;
