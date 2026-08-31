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

Tabelas adicionais previstas no escopo completo (conhecimento/RAG, uso de IA, integrações,
notificações) entram nos dias 4–6, conforme `TODO.md`, para manter cada migration pequena e
revisável.

## RLS

Toda tabela de domínio tem RLS habilitado com policy baseada em:

```sql
organization_id in (
  select organization_id from organization_users where user_id = auth.uid()
)
```

O backend usa a `service_role` key apenas em operações administrativas server-side; requests de
usuário devem, sempre que possível, respeitar RLS.
