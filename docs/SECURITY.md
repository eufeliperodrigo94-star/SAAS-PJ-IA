# SECURITY.md — Revisão de segurança (Dia 7)

Resumo do que foi verificado e corrigido na revisão de segurança do MVP, e das limitações
conhecidas que ficam para depois do MVP.

## O que foi verificado (sem necessidade de mudança)

- **RLS habilitado em todas as tabelas do domínio** (16 tabelas: organizations, users,
  organization_users, plans, subscriptions, companies, company_partners, company_addresses,
  company_activities, company_events, processes, documents, rules, validations, ai_usage,
  audit_logs) via `is_org_member()`. O backend usa a `service_role` key (que ignora RLS), então
  RLS aqui é defesa em profundidade — a aplicação real do isolamento é a filtragem explícita por
  `organization_id` em toda função de repositório.
- **Autenticação/autorização em todas as rotas de negócio**: nenhuma rota fora de `/health` e
  `/auth/*` (registro/login delegado ao Supabase Auth) está desprotegida — todas dependem de
  `require_organization` (ou `require_roles`, ver abaixo).
- **JWT do Supabase**: suporta tanto o esquema legado (HS256 + segredo compartilhado) quanto o
  atual (ES256/RS256 assinado por chave assimétrica, validado via JWKS público do projeto) — ver
  `app/core/security.py` e `ARCHITECTURE.md`.
- **CORS** restrito às origens definidas em `CORS_ORIGINS` (nunca `*`).
- **Segredos**: `.env` no `.gitignore`, `.env.example` só com placeholders, nenhuma chave
  (`service_role`, `ANTHROPIC_API_KEY`, JWT secret) versionada ou logada.
- **Logging estruturado** (`app/core/logging.py`) não grava corpo de requisição/resposta nem
  payloads de auth — apenas metadados (rota, status, duração).
- **Erros nunca vazam detalhes internos**: exceções não tratadas caem em
  `unhandled_error_handler`, que sempre responde com uma mensagem genérica (nunca stack trace,
  query SQL ou erro do provider de IA).

## O que foi corrigido nesta revisão

1. **Sanitização de nome de arquivo no upload de documentos**
   (`app/repositories/documents_repo._sanitize_filename`). Antes, o `filename` enviado pelo
   cliente ia direto para a chave do objeto no Storage. Agora: mantém só o último segmento do
   caminho (um `../../etc/passwd` vira `passwd`), substitui qualquer caractere fora de
   `[A-Za-z0-9._-]` por `_`, e limita a 200 caracteres. Mitiga path traversal / nomes malformados
   — na prática o Supabase Storage usa um namespace plano por bucket, mas é higiene básica de
   entrada não confiável. Testado em `tests/test_documents_repo_sanitize.py`.
2. **Controle de papéis (RBAC) além de "pertence à organização"**
   (`app/core/security.require_roles`). A troca de plano
   (`POST /subscriptions/change-plan`) — a ação de billing mais sensível hoje exposta — agora
   exige papel `owner` ou `admin`; antes qualquer membro da organização (inclusive `viewer`)
   podia trocar o plano. Testado em `tests/test_require_roles.py` e, via API, em
   `tests/test_integration_isolation.py`.

## Testes de integração adicionados

`tests/test_integration_isolation.py` usa `TestClient` + `dependency_overrides` (sem tocar em
banco real) para validar, através das rotas HTTP e não só das funções de serviço isoladas:

- rota protegida sem token → `401`;
- duas organizações diferentes só enxergam suas próprias empresas (`GET /companies`) e não
  conseguem buscar empresa de outra organização por id (`GET /companies/{id}` → `404`, nunca
  vazando existência do recurso);
- upload de documento acima de 10 MB → `413`;
- troca de plano por `viewer` → `403`; por `owner` → `200`;
- `/health` segue público.

## Painel super-admin da plataforma

Adicionado após o Dia 7: uma flag `users.is_super_admin` (migration `0005_platform_admin.sql`)
e uma dependência `require_super_admin` (`app/core/security.py`) protegendo as rotas `/admin/*`
(`app/api/admin.py`) — listar todas as organizações com plano/contadores, ver os usuários de
qualquer organização, trocar o plano de qualquer organização e ver métricas globais de IA. É
deliberadamente ortogonal ao RBAC por organização (`organization_role`): um super admin não
precisa pertencer a nenhuma organização para usar essas rotas. Promoção a super admin é manual
via SQL — não existe endpoint para isso, para não abrir uma via de escalonamento de privilégio
pela própria API. Coberto por testes unitários (`test_require_super_admin.py`,
`test_admin_service.py`) e de integração (`test_integration_isolation.py`: rota `/admin/*`
bloqueada para usuário comum, liberada para super admin).

## Limitações conhecidas (fora do escopo do MVP)

- **Sem rate limiting nos endpoints que chamam IA** (`POST /documents/{id}/extract`,
  `POST /assistant/message`). Hoje nada impede um usuário autenticado de gerar custo de IA em
  volume. Mitigação recomendada antes de abrir para muitos clientes: limitar por organização
  (ex.: contagem em `ai_usage` nos últimos N minutos) ou usar um rate limiter na borda (Render/
  API gateway).
- **`NullBillingProvider`**: troca de plano não cobra de fato — não há gateway de pagamento
  integrado ainda (ver `app/billing/provider.py`).
- **Frontend ainda não usa o visual aprovado no Claude Design** (canvas publicado, reimplementação
  pendente de confirmação para retomar).
