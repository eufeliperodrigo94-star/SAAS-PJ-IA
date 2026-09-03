# DATABASE.md

Schema Supabase/PostgreSQL. Migrations em `supabase/migrations/`. Toda tabela de domínio tem
`id uuid`, `created_at`, `updated_at` e (exceto `organizations`) `organization_id` para isolamento
multi-tenant via RLS.

## Dia 1 — tabelas fundamentais (`0001_init.sql`)

| Tabela | Descrição |
|---|---|
| `organizations` | Escritório/tenant. |
| `users` | Perfil espelhando `auth.users` (nome, email, avatar). |
| `organization_users` | Vínculo usuário↔organização + `role` (owner/admin/operator/viewer). |
| `plans` | Planos comerciais (Starter, Profissional, Escritório, Enterprise) e limites. |
| `subscriptions` | Assinatura ativa de uma organização (plano, status, período). |
| `companies` | Empresa cadastrada pelo escritório (CNPJ, razão social, natureza jurídica...). |
| `processes` | Processo de abertura/alteração de uma empresa (status, tipo). |
| `documents` | Documento anexado a um processo (metadados; arquivo no Supabase Storage). |
| `rules` | Regra determinística versionada (UF, tipo de processo, condição, severidade...). |
| `validations` | Resultado da execução do motor de regras sobre um processo. |
| `audit_logs` | Log de auditoria (quem fez o quê, quando, em qual organização). |

## Dia 2 — detalhamento de empresas (`0002_companies_detail.sql`)

| Tabela | Descrição |
|---|---|
| `company_partners` | Sócios da empresa (nome, CPF/CNPJ, qualificação, % capital, datas). |
| `company_addresses` | Endereços da empresa (sede/filial), com flag `atual` para histórico. |
| `company_activities` | CNAEs vinculados à empresa, com flag `is_primary`. |

`companies` ganhou a coluna `capital_social`.

## Dia 3 — memória empresarial (`0003_company_events.sql`)

| Tabela | Descrição |
|---|---|
| `company_events` | Timeline de eventos da empresa (criação, sócio/endereço/CNAE adicionado, processo iniciado etc.), com `payload jsonb` e `process_id` opcional. |

Toda mutação relevante em `companies`, `company_partners`, `company_addresses`,
`company_activities` e `processes` gera um `company_event`. O módulo `app/memory/company_memory.py`
agrega empresa + sócios + endereços + CNAEs + eventos recentes num único instantâneo
(`GET /companies/{id}/memory`), reutilizado ao iniciar novos processos — sem depender da LLM
para "lembrar" nada (ver `AI.md`).

## Dia 4 — motor de regras

Sem migration nova: `rules` e `validations` já existiam desde o Dia 1. `supabase/seed/seed.sql`
ganhou 4 regras reais para PE (`PE-CNAE-001`, `PE-END-001`, `PE-QSA-001`, `PE-QSA-002`), cada
uma com um `condicao.check` implementado em `app/rules/checks.py` — ver `RULES.md`.
`POST /processes/{id}/validate` substitui as `validations` do processo a cada execução e
atualiza `processes.status` (`pendente_correcao` / `pronto_para_protocolo` / `em_validacao`).

## Dia 5 — IA e documentos (`0004_ai_documents.sql`)

| Tabela | Descrição |
|---|---|
| `ai_usage` | Uma linha por chamada de IA: organização, processo, usuário, tarefa, provider, modelo, tokens de entrada/saída, latência, sucesso/erro. |

`documents` ganhou `extracted_data jsonb` e `extracted_at`. Criado o bucket privado `documents`
no Supabase Storage (caminho `"{organization_id}/{process_id}/{arquivo}"`), com policies de
`storage.objects` que reusam `is_org_member()` sobre o primeiro segmento do caminho.

## Dia 6 — dashboard, relatório e assinatura

Sem migration nova: `plans` e `subscriptions` já existiam desde o Dia 1. `app/billing/` ganha a
interface `BillingProvider` (ver `PROJECT.md`) e `app/services/billing_service.py` passa a criar
automaticamente uma assinatura `trialing` no plano Starter ao registrar uma organização
(`ensure_default_subscription`), além de bloquear a criação de empresas acima do
`plans.max_companies` do plano ativo. `GET /dashboard/summary` agora calcula números reais
(processos por status, validações por resultado, consumo de IA nos últimos 30 dias, plano
atual) e `GET /processes/{id}/report` monta o relatório de pré-validação a partir das
`validations` já persistidas — sem rodar regras novas nem chamar IA.

Tabelas adicionais previstas no escopo completo (conhecimento/RAG, integrações, notificações)
entram no Dia 7, conforme `TODO.md`, para manter cada migration pequena e revisável.

## Painel super-admin da plataforma (`0005_platform_admin.sql`)

`users` ganhou a coluna `is_super_admin boolean` (default `false`). Não é um papel de
`organization_role` — é ortogonal a qualquer organização e habilita as rotas `/admin/*`
(`app/api/admin.py`, protegidas por `require_super_admin` em `app/core/security.py`), que listam
todas as organizações, o detalhe de usuários de qualquer uma delas, trocam o plano de qualquer
organização e mostram métricas globais (organizações, empresas, processos, consumo de IA). Sem
policy de RLS nova: o backend usa a `service_role` key e faz essa checagem no próprio código.
Promover alguém a super admin hoje é manual (`update users set is_super_admin = true where id = ...`)
— não há UI para isso, de propósito, dado o alcance da permissão.

## Suporte, vendas e planos ativáveis (`0006_admin_extras.sql`)

| Tabela | Descrição |
|---|---|
| `support_tickets` | Chamado de suporte aberto por um membro da organização (assunto, status: aberto/em_andamento/resolvido/fechado, prioridade). |
| `support_ticket_messages` | Mensagens de um chamado (thread), com `author_is_admin` distinguindo resposta do super admin da do cliente. |

RLS igual ao padrão do resto do sistema (`is_org_member(organization_id)`): qualquer membro da
organização abre e responde os próprios chamados via `/support/*`. O painel admin
(`/admin/support/*`) vê e responde chamados de qualquer organização — via `service_role`, RLS não
entra em jogo ali.

`plans` ganhou a coluna `active boolean` (default `true`): um plano pode ser descontinuado
(`active = false`) sem afetar organizações já assinantes dele. `GET /plans` (rota pública)
só lista planos ativos; `GET /admin/plans` lista todos. "Vendas" não é uma tabela nova — 
`GET /admin/sales` (`app/services/admin_service.get_sales_summary`) calcula MRR, contagem de
assinaturas ativas/trial e conversão diretamente de `subscriptions` + `plans`, já existentes
desde o Dia 1.

## RLS

Toda tabela de domínio tem RLS habilitado com policy baseada em:

```sql
organization_id in (
  select organization_id from organization_users where user_id = auth.uid()
)
```

O backend usa a `service_role` key apenas em operações administrativas server-side; requests de
usuário devem, sempre que possível, respeitar RLS.
