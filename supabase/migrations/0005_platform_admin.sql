-- 0005_platform_admin.sql
-- Painel super-admin da plataforma: uma flag em `users` identifica quem pode
-- administrar todas as organizações (fora do isolamento multi-tenant normal).
-- O backend usa a service_role key (ignora RLS) e faz essa checagem no
-- próprio código (app/core/security.py), então nenhuma policy nova é
-- necessária aqui — só o dado.

alter table users add column is_super_admin boolean not null default false;
