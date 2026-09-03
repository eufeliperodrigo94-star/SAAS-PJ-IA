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

## Deploy (Render + Vercel)

**Backend (Render)** — `render.yaml` já descreve o serviço (Docker, `backend/Dockerfile`):

1. Crie uma conta em [render.com](https://render.com) e conecte este repositório GitHub.
2. "New +" → "Blueprint" → selecione o repositório; o Render lê `render.yaml` automaticamente.
3. Preencha no dashboard (aba Environment) as variáveis marcadas `sync: false`:
   `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`, `ANTHROPIC_API_KEY`
   (os mesmos valores do seu `.env`).
4. Após o deploy, o Render expõe uma URL pública (`https://<nome-do-serviço>.onrender.com`).

**Frontend (Vercel)** — `vercel.json` serve a pasta `frontend/` como raiz do site:

1. Atualize `frontend/assets/config.js` com a URL pública do backend no Render
   (`API_BASE_URL`) e faça commit/push — o Vercel já está conectado a este repositório e
   redeploya automaticamente a cada push.
2. Atualize `CORS_ALLOW_ORIGINS` no Render (ou em `render.yaml`) com o domínio real do Vercel.

**Painel admin em URL separada (opcional)** — o painel super-admin (`admin.html`) já funciona
dentro do mesmo site, mas para dar a ele uma "porta de entrada" própria (útil antes de ter um
domínio próprio, e pronto para virar `admin.seudominio.com` depois):

1. No dashboard da Vercel, "Add New..." → "Project" → selecione este mesmo repositório GitHub
   de novo (dá para conectar o mesmo repo a mais de um projeto Vercel).
2. Em "Root Directory" desse novo projeto, escolha `frontend` (em vez da raiz do repositório).
   A Vercel vai usar `frontend/vercel.json` — que só redireciona `/` para `admin.html` — em vez
   do `vercel.json` da raiz (que redireciona `/` para `login.html`).
3. Configure as mesmas variáveis/`assets/config.js` (é o mesmo build, só muda a página inicial).
4. Isso cria uma segunda URL `.vercel.app` (ex.: `saas-pj-ia-admin.vercel.app`) cuja página
   inicial já é o painel admin. **Isso é só conveniência de URL, não é uma barreira de
   segurança** — a proteção de verdade continua sendo `require_super_admin` no backend; qualquer
   página do site continua acessível pelo nome de arquivo em qualquer um dos dois projetos.
5. Quando comprar um domínio próprio, aponte `admin.seudominio.com` para este segundo projeto e
   `app.seudominio.com` (ou o domínio raiz) para o projeto original.

## Documentação

Veja `docs/` para arquitetura, banco de dados, motor de regras, uso de IA e a revisão de
segurança (`docs/SECURITY.md`).

## Status

MVP dos 7 dias concluído (ver `docs/TODO.md`): autenticação e multi-tenant, empresas/sócios/
endereços/CNAEs/processos, memória empresarial (timeline), motor de regras determinístico,
documentos + extração e cruzamento via IA + assistente em linguagem natural, dashboard +
relatório de pré-validação + assinatura/planos, e revisão de segurança + testes de integração de
isolamento multi-tenant. Deploy em produção: Render (backend) + Vercel (frontend) + Supabase
(banco/auth/storage). 69 testes automatizados passando (`pytest -q` em `backend/`).
