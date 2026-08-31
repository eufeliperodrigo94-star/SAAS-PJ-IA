-- 0001_init.sql
-- Dia 1: fundação — organizações, usuários, empresas, processos, documentos,
-- validações, regras e assinaturas. Multi-tenant com isolamento por organização (RLS).

create extension if not exists "pgcrypto";

-- ---------------------------------------------------------------------------
-- organizations / users / organization_users
-- ---------------------------------------------------------------------------

create table organizations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text unique,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Perfil espelhando auth.users (nome/email adicionais que o Supabase Auth não guarda por si).
create table users (
  id uuid primary key references auth.users (id) on delete cascade,
  full_name text,
  email text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create type organization_role as enum ('owner', 'admin', 'operator', 'viewer');

create table organization_users (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations (id) on delete cascade,
  user_id uuid not null references users (id) on delete cascade,
  role organization_role not null default 'operator',
  created_at timestamptz not null default now(),
  unique (organization_id, user_id)
);

create index idx_organization_users_user_id on organization_users (user_id);
create index idx_organization_users_org_id on organization_users (organization_id);

-- ---------------------------------------------------------------------------
-- plans / subscriptions
-- ---------------------------------------------------------------------------

create table plans (
  id uuid primary key default gen_random_uuid(),
  code text unique not null,
  name text not null,
  max_companies integer,
  price_cents integer,
  created_at timestamptz not null default now()
);

create type subscription_status as enum ('trialing', 'active', 'past_due', 'canceled');

create table subscriptions (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations (id) on delete cascade,
  plan_id uuid not null references plans (id),
  status subscription_status not null default 'trialing',
  current_period_start timestamptz,
  current_period_end timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_subscriptions_org_id on subscriptions (organization_id);

-- ---------------------------------------------------------------------------
-- companies / processes / documents
-- ---------------------------------------------------------------------------

create table companies (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations (id) on delete cascade,
  cnpj text,
  razao_social text not null,
  nome_fantasia text,
  natureza_juridica text,
  uf text,
  municipio text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (organization_id, cnpj)
);

create index idx_companies_org_id on companies (organization_id);

create type process_type as enum (
  'abertura',
  'alteracao_qsa',
  'alteracao_endereco',
  'alteracao_cnae',
  'alteracao_capital',
  'alteracao_administrador',
  'alteracao_nome_objeto'
);

create type process_status as enum (
  'rascunho',
  'em_validacao',
  'pendente_correcao',
  'pronto_para_protocolo',
  'protocolado',
  'arquivado'
);

create table processes (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations (id) on delete cascade,
  company_id uuid not null references companies (id) on delete cascade,
  type process_type not null,
  status process_status not null default 'rascunho',
  description text,
  created_by uuid references users (id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_processes_org_id on processes (organization_id);
create index idx_processes_company_id on processes (company_id);

create table documents (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations (id) on delete cascade,
  process_id uuid not null references processes (id) on delete cascade,
  file_name text not null,
  storage_path text not null,
  content_type text,
  uploaded_by uuid references users (id),
  created_at timestamptz not null default now()
);

create index idx_documents_org_id on documents (organization_id);
create index idx_documents_process_id on documents (process_id);

-- ---------------------------------------------------------------------------
-- rules / validations
-- ---------------------------------------------------------------------------

create type rule_severity as enum ('ok', 'atencao', 'erro');

create table rules (
  id uuid primary key default gen_random_uuid(),
  codigo text unique not null,
  nome text not null,
  descricao text,
  uf text,
  municipio text,
  tipo_processo process_type,
  condicao jsonb not null default '{}'::jsonb,
  severidade rule_severity not null,
  mensagem text not null,
  acao_sugerida text,
  fonte text,
  versao integer not null default 1,
  vigencia_inicio date,
  vigencia_fim date,
  ativo boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_rules_uf_tipo on rules (uf, tipo_processo);

create table validations (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations (id) on delete cascade,
  process_id uuid not null references processes (id) on delete cascade,
  rule_id uuid references rules (id),
  result rule_severity not null,
  evidence jsonb not null default '{}'::jsonb,
  message text not null,
  suggested_action text,
  created_at timestamptz not null default now()
);

create index idx_validations_org_id on validations (organization_id);
create index idx_validations_process_id on validations (process_id);

-- ---------------------------------------------------------------------------
-- audit_logs
-- ---------------------------------------------------------------------------

create table audit_logs (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid references organizations (id) on delete cascade,
  user_id uuid references users (id),
  action text not null,
  entity_type text,
  entity_id uuid,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index idx_audit_logs_org_id on audit_logs (organization_id);

-- ---------------------------------------------------------------------------
-- Row Level Security — isolamento multi-tenant
-- ---------------------------------------------------------------------------

alter table organizations enable row level security;
alter table users enable row level security;
alter table organization_users enable row level security;
alter table subscriptions enable row level security;
alter table companies enable row level security;
alter table processes enable row level security;
alter table documents enable row level security;
alter table validations enable row level security;
alter table audit_logs enable row level security;
-- plans e rules são catálogos globais (leitura liberada; escrita só via service_role/admin).
alter table plans enable row level security;
alter table rules enable row level security;

create or replace function is_org_member(target_org uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1 from organization_users ou
    where ou.organization_id = target_org
      and ou.user_id = auth.uid()
  );
$$;

create policy "org members can read their organization"
  on organizations for select
  using (is_org_member(id));

create policy "users can read own profile"
  on users for select
  using (id = auth.uid());

create policy "users can update own profile"
  on users for update
  using (id = auth.uid());

create policy "org members can read membership rows"
  on organization_users for select
  using (is_org_member(organization_id));

create policy "org members can read subscription"
  on subscriptions for select
  using (is_org_member(organization_id));

create policy "everyone can read active plans"
  on plans for select
  using (true);

create policy "everyone can read active rules"
  on rules for select
  using (ativo = true);

create policy "org members can manage companies"
  on companies for all
  using (is_org_member(organization_id))
  with check (is_org_member(organization_id));

create policy "org members can manage processes"
  on processes for all
  using (is_org_member(organization_id))
  with check (is_org_member(organization_id));

create policy "org members can manage documents"
  on documents for all
  using (is_org_member(organization_id))
  with check (is_org_member(organization_id));

create policy "org members can read validations"
  on validations for select
  using (is_org_member(organization_id));

create policy "org members can read audit logs"
  on audit_logs for select
  using (is_org_member(organization_id));
