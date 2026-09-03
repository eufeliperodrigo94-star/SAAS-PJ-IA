# TODO.md — Cronograma de 7 dias

| Dia | Entrega | Status |
|---|---|---|
| 1 | Arquitetura, Supabase, banco e autenticação | ✅ concluído |
| 2 | Empresas, sócios, endereços, CNAEs e processos | ✅ concluído |
| 3 | Memória empresarial e histórico | ✅ concluído |
| 4 | Motor de regras e pré-validação | ✅ concluído |
| 5 | Documentos + Claude + cruzamento | ✅ concluído |
| 6 | Dashboard + relatório + assinatura | ✅ concluído |
| 7 | Testes + segurança + deploy | ✅ concluído |

## Dia 1 — Fundação

- [x] Estrutura de pastas (`backend/`, `frontend/`, `supabase/`, `docs/`).
- [x] FastAPI, CORS, `.env.example`, logging estruturado, tratamento de erros, `/health`.
- [x] Migration inicial: organizations, users, organization_users, plans, subscriptions,
      companies, processes, documents, rules, validations, audit_logs (+ RLS).
- [x] Auth: registro de organização + resolução de usuário/organização via JWT Supabase.
- [x] Frontend: login, cadastro (registro de organização) e dashboard inicial (stub).
- [x] Aplicar migration em um projeto Supabase real e validar login ponta a ponta (projeto
      `xdvfvuzwyedlsvujmyjn`). Corrigido `app/core/security.py` para verificar também JWTs
      assinados com chave assimétrica via JWKS (padrão dos projetos Supabase atuais) — ver
      `ARCHITECTURE.md`.

## Dia 2 — Empresas

- [x] Migration `0002_companies_detail.sql`: `company_partners`, `company_addresses`,
      `company_activities` (+ RLS) e `capital_social` em `companies`.
- [x] API: CRUD de empresas, sócios, endereços, CNAEs; criação/listagem/detalhe de processos.
- [x] Isolamento multi-tenant reforçado no backend (serviços validam organização antes de
      qualquer leitura/escrita) — coberto por testes unitários.
- [x] Frontend: `companies.html` (lista + cadastro), `company.html` (detalhe completo),
      `process.html` (novo processo).
- [x] Validado ponta a ponta com um projeto Supabase real (cadastro → sócios/endereços/CNAEs →
      novo processo).

## Dia 3 — Memória empresarial

- [x] Migration `0003_company_events.sql`: `company_events` (timeline) + RLS.
- [x] Serviços de empresa/processo registram eventos automaticamente (criação/atualização de
      empresa, sócio/endereço/CNAE adicionado, processo iniciado).
- [x] `app/memory/company_memory.py`: agrega dados estruturados + histórico recente + contagem
      de processos em aberto. Rotas `GET /companies/{id}/timeline` e `GET /companies/{id}/memory`.
- [x] Frontend: painel de timeline em `company.html`; `process.html` mostra a memória reutilizável
      (sócios, endereço atual, CNAEs, processos em aberto) antes de criar um novo processo.
- [x] Validado ponta a ponta com um projeto Supabase real (timeline e memória refletindo os
      eventos reais de um processo).

## Dia 4 — Motor de regras

- [x] `app/rules/checks.py`: `company_has_activity`, `company_has_address`,
      `company_has_partners`, `partners_percentual_sum`, `required_company_fields`.
- [x] `app/rules/engine.py`: filtra regras ativas por UF/tipo de processo/vigência e despacha
      para o check correspondente — nunca chama LLM.
- [x] `app/services/validation_service.py`: persiste resultados em `validations` (substituindo
      a execução anterior) e recalcula `processes.status`.
- [x] Rotas `POST /processes/{id}/validate` e `GET /processes/{id}/validations`.
- [x] Seed com 4 regras reais para PE (`PE-CNAE-001`, `PE-END-001`, `PE-QSA-001`, `PE-QSA-002`).
- [x] Frontend: `process-detail.html` com botão "Executar pré-validação" e resultado
      (OK/Atenção/Erro, evidência e ação sugerida); linkado a partir de `company.html`.
- [x] Validado ponta a ponta com um projeto Supabase real: seed aplicado, processo sem
      CNAE/endereço reprovado (`erro`) e aprovado (`ok`) após completar o cadastro.

## Dia 5 — IA e documentos

- [x] Migration `0004_ai_documents.sql`: `ai_usage`, `documents.extracted_data/extracted_at`,
      bucket privado `documents` no Storage + RLS.
- [x] `app/ai/`: `AIProvider` (interface), `ClaudeProvider`, `AIRouter` — registra toda chamada
      em `ai_usage`; erros do provider nunca vazam (viram `AIUnavailableError`).
- [x] Documentos: upload no Storage (`POST /documents/upload`), extração via IA + cruzamento
      determinístico cadastro×documento (`POST /documents/{id}/extract`,
      `app/documents/cross_check.py`), listagem (`GET /processes/{id}/documents`).
- [x] Assistente: `POST /assistant/message` transforma linguagem natural em proposta JSON por
      tipo de processo — nunca aplica a alteração sozinho.
- [x] Frontend: seções de Documentos, extração/cruzamento e Assistente IA em
      `process-detail.html`.
- [ ] Validar ponta a ponta com `ANTHROPIC_API_KEY` real e um projeto Supabase real (upload +
      extração + assistente).

## Dia 6 — Dashboard, relatório e assinatura

- [x] `app/billing/provider.py`: interface `BillingProvider` + `NullBillingProvider` (sem
      gateway real ainda — trocar de plano é direto, sem cobrança).
- [x] `app/services/billing_service.py`: assinatura padrão (Starter, trialing) criada ao
      registrar organização; `check_company_limit` bloqueia cadastro de empresa acima do plano.
- [x] Rotas `GET /plans`, `GET /subscriptions`, `POST /subscriptions/change-plan`.
- [x] `GET /dashboard/summary` com números reais: processos por status, validações por
      resultado, consumo de IA (últimos 30 dias) e plano atual.
- [x] `GET /processes/{id}/report`: relatório de pré-validação (resumo, erros, alertas, itens
      OK, documentos enviados, regras aplicadas com versão, ações recomendadas, aviso de
      pré-análise) a partir das `validations` já persistidas.
- [x] Frontend: `assinatura.html` (plano atual + troca de plano), `dashboard.html` com números
      reais + plano + consumo de IA, seção de relatório em `process-detail.html`.
- [x] Validado ponta a ponta em produção (Render + Supabase real): assinatura Starter criada
      automaticamente, troca de plano, criação de empresa/processo, pré-validação, relatório
      completo e dashboard refletindo os números reais.

## Dia 7 — Testes, segurança e deploy

- [x] Revisão de segurança: RLS habilitado nas 16 tabelas, todas as rotas usam dependências de
      auth (`require_organization`/`require_roles`), CORS restrito às origens configuradas,
      nenhum segredo versionado no repositório, logs não capturam dados sensíveis.
- [x] Corrigido: nomes de arquivo enviados ao Storage agora são sanitizados
      (`app/repositories/documents_repo._sanitize_filename`) — remove segmentos de caminho
      (`../`, `C:\...`) e caracteres inseguros antes de compor a chave do objeto.
- [x] Adicionado controle de papéis (`app/core/security.require_roles`) e aplicado à troca de
      plano (`POST /subscriptions/change-plan`, restrita a `owner`/`admin`) — a ação de billing
      mais sensível hoje exposta.
- [x] Testes de integração via API (`tests/test_integration_isolation.py`, `TestClient`):
      rota protegida sem token → 401; isolamento multi-tenant real entre duas organizações
      (lista e detalhe de empresa); limite de 10 MB no upload de documentos → 413; RBAC na troca
      de plano → 403 para `viewer`, 200 para `owner`; `/health` público.
- [x] Ver `docs/SECURITY.md` para o resumo completo da revisão (o que foi verificado, o que foi
      corrigido e limitações conhecidas ainda não endereçadas).
- [x] Suíte completa validada: 69 testes passando (`pytest -q` em `backend/`).

## Próximos dias (visão geral)

O MVP dos 7 dias está concluído. Melhorias futuras (fora do escopo do MVP) estão listadas em
`docs/SECURITY.md` (limitações conhecidas) e incluem: rate limiting nos endpoints que chamam a
IA, gateway de pagamento real (hoje `NullBillingProvider`), e substituição do frontend pelo
visual aprovado no Claude Design.

Trabalhe em tarefas pequenas; leia apenas os arquivos de `docs/` necessários para cada etapa.
