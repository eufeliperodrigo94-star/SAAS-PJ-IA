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

Tabelas adicionais previstas no escopo completo (histórico de eventos/timeline,
conhecimento/RAG, uso de IA, integrações, notificações) entram nos dias 3–6, conforme
`TODO.md`, para manter cada migration pequena e revisável.

## RLS

Toda tabela de domínio tem RLS habilitado com policy baseada em:

```sql
organization_id in (
  select organization_id from organization_users where user_id = auth.uid()
)
```

O backend usa a `service_role` key apenas em operações administrativas server-side; requests de
usuário devem, sempre que possível, respeitar RLS.
