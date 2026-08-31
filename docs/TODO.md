# TODO.md — Cronograma de 7 dias

| Dia | Entrega | Status |
|---|---|---|
| 1 | Arquitetura, Supabase, banco e autenticação | ✅ em andamento |
| 2 | Empresas, sócios, endereços, CNAEs e processos | ⬜ |
| 3 | Memória empresarial e histórico | ⬜ |
| 4 | Motor de regras e pré-validação | ⬜ |
| 5 | Documentos + Claude + cruzamento | ⬜ |
| 6 | Dashboard + relatório + assinatura | ⬜ |
| 7 | Testes + segurança + deploy | ⬜ |

## Dia 1 — Fundação

- [x] Estrutura de pastas (`backend/`, `frontend/`, `supabase/`, `docs/`).
- [x] FastAPI, CORS, `.env.example`, logging estruturado, tratamento de erros, `/health`.
- [x] Migration inicial: organizations, users, organization_users, plans, subscriptions,
      companies, processes, documents, rules, validations, audit_logs (+ RLS).
- [x] Auth: registro de organização + resolução de usuário/organização via JWT Supabase.
- [x] Frontend: login, cadastro (registro de organização) e dashboard inicial (stub).
- [ ] Aplicar migration em um projeto Supabase real e validar login ponta a ponta.

## Próximos dias (visão geral)

- **Dia 2:** CRUD de empresas (sócios, endereços, CNAEs) e processos; telas Minhas
  Empresas/Nova Empresa/Detalhe.
- **Dia 3:** Timeline/memória por empresa reutilizada em novos processos.
- **Dia 4:** `rules/engine.py`, validators e regras iniciais para PE; resultados OK/ATENÇÃO/ERRO.
- **Dia 5:** AI Router + Claude provider; upload/extração/comparação de documentos.
- **Dia 6:** Dashboard completo, relatório de pré-validação, planos e billing.
- **Dia 7:** Testes automatizados, revisão de segurança/RLS, Dockerfile de produção e deploy.

Trabalhe em tarefas pequenas; leia apenas os arquivos de `docs/` necessários para cada etapa.
