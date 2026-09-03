-- 0004_ai_documents.sql
-- Dia 5: AI Router (uso/custo por chamada), extração de documentos e storage.

create table ai_usage (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations (id) on delete cascade,
  process_id uuid references processes (id) on delete set null,
  user_id uuid references users (id),
  task text not null,
  provider text not null,
  model text not null,
  tokens_input integer,
  tokens_output integer,
  latency_ms integer,
  success boolean not null default true,
  error_message text,
  created_at timestamptz not null default now()
);

create index idx_ai_usage_org_id on ai_usage (organization_id);
create index idx_ai_usage_process_id on ai_usage (process_id);

alter table ai_usage enable row level security;

create policy "org members can read their ai usage"
  on ai_usage for select
  using (is_org_member(organization_id));

-- `documents` (Dia 1) ganha o resultado da extração (Camada 5 — LLM sob demanda).
alter table documents add column if not exists extracted_data jsonb;
alter table documents add column if not exists extracted_at timestamptz;

-- ---------------------------------------------------------------------------
-- Storage: bucket privado para os documentos dos processos.
-- Caminho de cada objeto: "{organization_id}/{process_id}/{filename}" — a RLS
-- usa o primeiro segmento do caminho para checar a organização do usuário.
-- ---------------------------------------------------------------------------

insert into storage.buckets (id, name, public)
values ('documents', 'documents', false)
on conflict (id) do nothing;

create policy "org members can read their documents"
  on storage.objects for select
  using (
    bucket_id = 'documents'
    and is_org_member((storage.foldername(name))[1]::uuid)
  );

create policy "org members can upload their documents"
  on storage.objects for insert
  with check (
    bucket_id = 'documents'
    and is_org_member((storage.foldername(name))[1]::uuid)
  );
