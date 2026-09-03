-- 0003_company_events.sql
-- Dia 3: memória empresarial — timeline de eventos por empresa.
-- Fica inteiramente no Postgres/Supabase; não é enviada para a LLM por padrão
-- (ver docs/AI.md — regra de ouro: recuperar só o contexto relevante).

create table company_events (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations (id) on delete cascade,
  company_id uuid not null references companies (id) on delete cascade,
  process_id uuid references processes (id) on delete set null,
  event_type text not null,
  description text not null,
  payload jsonb not null default '{}'::jsonb,
  created_by uuid references users (id),
  created_at timestamptz not null default now()
);

create index idx_company_events_org_id on company_events (organization_id);
create index idx_company_events_company_id on company_events (company_id, created_at desc);

alter table company_events enable row level security;

create policy "org members can manage company events"
  on company_events for all
  using (is_org_member(organization_id))
  with check (is_org_member(organization_id));
