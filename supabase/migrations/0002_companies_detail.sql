-- 0002_companies_detail.sql
-- Dia 2: sócios, endereços e CNAEs por empresa.

alter table companies add column if not exists capital_social numeric(18, 2);

-- ---------------------------------------------------------------------------
-- company_partners (sócios)
-- ---------------------------------------------------------------------------

create table company_partners (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations (id) on delete cascade,
  company_id uuid not null references companies (id) on delete cascade,
  nome text not null,
  cpf_cnpj text,
  qualificacao text,
  percentual_capital numeric(5, 2),
  data_entrada date,
  data_saida date,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_company_partners_org_id on company_partners (organization_id);
create index idx_company_partners_company_id on company_partners (company_id);

-- ---------------------------------------------------------------------------
-- company_addresses (endereços)
-- ---------------------------------------------------------------------------

create type address_type as enum ('sede', 'filial');

create table company_addresses (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations (id) on delete cascade,
  company_id uuid not null references companies (id) on delete cascade,
  tipo address_type not null default 'sede',
  logradouro text,
  numero text,
  complemento text,
  bairro text,
  municipio text,
  uf text,
  cep text,
  atual boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_company_addresses_org_id on company_addresses (organization_id);
create index idx_company_addresses_company_id on company_addresses (company_id);

-- ---------------------------------------------------------------------------
-- company_activities (CNAEs)
-- ---------------------------------------------------------------------------

create table company_activities (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations (id) on delete cascade,
  company_id uuid not null references companies (id) on delete cascade,
  cnae_code text not null,
  description text,
  is_primary boolean not null default false,
  created_at timestamptz not null default now(),
  unique (company_id, cnae_code)
);

create index idx_company_activities_org_id on company_activities (organization_id);
create index idx_company_activities_company_id on company_activities (company_id);

-- ---------------------------------------------------------------------------
-- RLS — mesmo padrão multi-tenant das demais tabelas de domínio
-- ---------------------------------------------------------------------------

alter table company_partners enable row level security;
alter table company_addresses enable row level security;
alter table company_activities enable row level security;

create policy "org members can manage company partners"
  on company_partners for all
  using (is_org_member(organization_id))
  with check (is_org_member(organization_id));

create policy "org members can manage company addresses"
  on company_addresses for all
  using (is_org_member(organization_id))
  with check (is_org_member(organization_id));

create policy "org members can manage company activities"
  on company_activities for all
  using (is_org_member(organization_id))
  with check (is_org_member(organization_id));
