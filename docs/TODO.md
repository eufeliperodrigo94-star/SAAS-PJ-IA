# TODO.md — Cronograma de 7 dias

| Dia | Entrega | Status |
|---|---|---|
| 1 | Arquitetura, Supabase, banco e autenticação | ✅ concluído |
| 2 | Empresas, sócios, endereços, CNAEs e processos | ✅ concluído |
| 3 | Memória empresarial e histórico | ✅ concluído |
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

## Dia 2 — Empresas

- [x] Migration `0002_companies_detail.sql`: `company_partners`, `company_addresses`,
      `company_activities` (+ RLS) e `capital_social` em `companies`.
- [x] API: CRUD de empresas, sócios, endereços, CNAEs; criação/listagem/detalhe de processos.
- [x] Isolamento multi-tenant reforçado no backend (serviços validam organização antes de
      qualquer leitura/escrita) — coberto por testes unitários.
- [x] Frontend: `companies.html` (lista + cadastro), `company.html` (detalhe completo),
      `process.html` (novo processo).
- [ ] Validar ponta a ponta com um projeto Supabase real (cadastro → sócios/endereços/CNAEs →
      novo processo).

## Dia 3 — Memória empresarial

- [x] Migration `0003_company_events.sql`: `company_events` (timeline) + RLS.
- [x] Serviços de empresa/processo registram eventos automaticamente (criação/atualização de
      empresa, sócio/endereço/CNAE adicionado, processo iniciado).
- [x] `app/memory/company_memory.py`: agrega dados estruturados + histórico recente + contagem
      de processos em aberto. Rotas `GET /companies/{id}/timeline` e `GET /companies/{id}/memory`.
- [x] Frontend: painel de timeline em `company.html`; `process.html` mostra a memória reutilizável
      (sócios, endereço atual, CNAEs, processos em aberto) antes de criar um novo processo.
- [ ] Validar ponta a ponta com um projeto Supabase real.

## Próximos dias (visão geral)

- **Dia 4:** `rules/engine.py`, validators e regras iniciais para PE; resultados OK/ATENÇÃO/ERRO.
- **Dia 5:** AI Router + Claude provider; upload/extração/comparação de documentos.
- **Dia 6:** Dashboard completo, relatório de pré-validação, planos e billing.
- **Dia 7:** Testes automatizados, revisão de segurança/RLS, Dockerfile de produção e deploy.

Trabalhe em tarefas pequenas; leia apenas os arquivos de `docs/` necessários para cada etapa.
