-- 0006_admin_extras.sql
-- Extensões do painel super-admin: suporte a clientes, base para vendas/MRR
-- (reaproveita subscriptions/plans já existentes) e planos ativáveis.

create type support_ticket_status as enum ('aberto', 'em_andamento', 'resolvido', 'fechado');
create type support_ticket_priority as enum ('baixa', 'normal', 'alta');

create table support_tickets (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organizations (id) on delete cascade,
  created_by uuid references users (id),
  subject text not null,
  status support_ticket_status not null default 'aberto',
  priority support_ticket_priority not null default 'normal',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_support_tickets_org_id on support_tickets (organization_id);
create index idx_support_tickets_status on support_tickets (status);

create table support_ticket_messages (
  id uuid primary key default gen_random_uuid(),
  ticket_id uuid not null references support_tickets (id) on delete cascade,
  organization_id uuid not null references organizations (id) on delete cascade,
  author_id uuid references users (id),
  author_is_admin boolean not null default false,
  body text not null,
  created_at timestamptz not null default now()
);

create index idx_support_ticket_messages_ticket_id on support_ticket_messages (ticket_id);

alter table support_tickets enable row level security;
alter table support_ticket_messages enable row level security;

-- Membros da organização veem e abrem tickets da própria organização; o
-- backend usa a service_role key para as rotas /admin/support/* (RLS não
-- entra em jogo ali — ver app/core/security.require_super_admin).
create policy "org members can manage their tickets"
  on support_tickets for all
  using (is_org_member(organization_id))
  with check (is_org_member(organization_id));

create policy "org members can manage their ticket messages"
  on support_ticket_messages for all
  using (is_org_member(organization_id))
  with check (is_org_member(organization_id));

-- Planos deixam de ser apenas ativos/globais: um plano pode ser descontinuado
-- (active = false) sem quebrar organizações que já estão nele.
alter table plans add column if not exists active boolean not null default true;
