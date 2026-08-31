# SaaS de Pré-Validação Empresarial (MVP — Pernambuco)

Copiloto para contadores e escritórios: identifica erros, divergências e documentos ausentes
antes do protocolo de processos empresariais (abertura, alteração de QSA, endereço, CNAE, capital
etc.). O sistema **não substitui** a Junta Comercial nem promete aprovação — ele reduz retrabalho.

> "Revise o processo antes de protocolar."

## Stack

- **Backend:** Python + FastAPI
- **Banco / Auth / Storage:** Supabase (PostgreSQL + Auth + Storage)
- **Frontend:** HTML5 + CSS3 + JavaScript vanilla (sem framework pesado)
- **IA:** AI Router com Claude API como provider padrão
- **Deploy:** Docker / Cloud Code

## Arquitetura

```
backend/
  app/
    main.py            # FastAPI app entrypoint
    core/               # config, logging, security (JWT), exceptions
    api/                # routers (auth, health, ...)
    models/             # domain models (dataclasses/pydantic)
    schemas/             # request/response schemas
    services/            # business logic
    repositories/         # Supabase/Postgres data access
    rules/                # motor de regras determinístico
    memory/               # memória em camadas (empresa/processo/regra/conhecimento)
    ai/                   # AI Router e providers (Claude, ...)
    integrations/         # adapters para órgãos externos (autorizados)
    billing/              # planos, assinaturas, BillingProvider
    documents/            # upload/extração/comparação de documentos
    notifications/        # e-mail/eventos
    audit/                # logs de auditoria
  tests/
frontend/
  index.html, login.html, dashboard.html, ...
  assets/
supabase/
  migrations/
  seed/
docs/
  PROJECT.md, ARCHITECTURE.md, DATABASE.md, RULES.md, AI.md, TODO.md
```

## Princípio central

A LLM **não** é o banco de memória nem o motor principal de regras.

1. Dados estruturados para fatos.
2. Motor determinístico para regras.
3. Histórico (Supabase/Postgres) para memória.
4. Busca/RAG para conhecimento.
5. LLM somente quando houver necessidade real de interpretação, extração, resumo ou explicação.

## Rodando localmente

```bash
cp .env.example .env   # preencha SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_JWT_SECRET, ANTHROPIC_API_KEY
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --reload --app-dir backend --port 8000
```

Aplique as migrations em `supabase/migrations/` no seu projeto Supabase (SQL editor ou `supabase db push`).

Sirva o `frontend/` com qualquer servidor estático (ex.: `python -m http.server 8080 --directory frontend`).

## Docker

```bash
docker compose up --build
```

## Documentação

Veja `docs/` para arquitetura, banco de dados, motor de regras e uso de IA.

## Status

Progresso seguindo `docs/TODO.md` (cronograma de 7 dias). Dia 1: fundação, banco e autenticação.
