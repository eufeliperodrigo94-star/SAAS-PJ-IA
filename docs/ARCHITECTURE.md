# ARCHITECTURE.md

## Camadas

```
Frontend (HTML/CSS/JS vanilla)
        │  fetch() + Supabase JS (auth)
        ▼
Backend (FastAPI)
  api/            → routers HTTP
  services/       → regras de negócio
  repositories/   → acesso a dados (Supabase/Postgres)
  rules/          → motor de regras determinístico
  memory/         → memória em camadas (empresa/processo/regra/conhecimento)
  ai/             → AI Router (Claude e outros providers)
  documents/      → upload/extração/comparação
  integrations/   → adapters externos autorizados
  billing/        → planos/assinaturas
  audit/          → logs de auditoria
        │
        ▼
Supabase (PostgreSQL + Auth + Storage, com RLS multi-tenant)
```

## Princípio central

A LLM não é banco de memória nem motor de regras. Ordem de resolução para qualquer solicitação:

1. **Dados estruturados** (Postgres) resolvem fatos.
2. **Motor de regras** determinístico resolve validações conhecidas.
3. **Histórico** (memória em camadas) fornece contexto sem reenviar tudo.
4. **Busca/RAG** recupera conhecimento normativo relevante.
5. **LLM** só entra para interpretação, extração difícil, explicação ou geração assistida.

## Multi-tenant

Toda tabela de domínio pertence a uma `organization_id`. Isolamento garantido em duas camadas:

- **RLS no Supabase** (política por `organization_id` via `organization_users`).
- **Validação no backend** (dependency injeta a organização do usuário autenticado; toda query
  filtra por ela).

Papéis: `owner`, `admin`, `operator`, `viewer`.

## Autenticação

- Supabase Auth emite o JWT (login/signup feitos no frontend via `supabase-js`).
- Backend valida o JWT em cada request (`app/core/security.py`) e resolve
  `user_id` → organizações e papel via `organization_users`. Suporta os dois esquemas de
  assinatura do Supabase: projetos legados usam HS256 com `SUPABASE_JWT_SECRET` (segredo
  compartilhado); projetos criados a partir de 2024 assinam com uma chave assimétrica
  (ES256/RS256) publicada em `{SUPABASE_URL}/auth/v1/.well-known/jwks.json` — o backend detecta
  o algoritmo pelo header do token e verifica contra a JWKS pública nesse caso, com cache e um
  refresh automático se o `kid` não for encontrado (rotação de chave).
- Registro de escritório: `POST /auth/register-organization` cria `organizations` +
  `organization_users` (papel `owner`) para o usuário Supabase já autenticado.

## AI Router

Interface única (`ai/base.py`: `AIProvider.generate/classify/extract/summarize`). Implementação
inicial: Claude (`ai/providers/claude_provider.py`). Escolha de modelo por tarefa/custo é
configurável via `core/config.py`, nunca hard-coded na lógica de negócio. Toda chamada registra
provider, modelo, tokens, latência e custo estimado (tabela `ai_usage`, adicionada no Dia 4/5).

## Deploy

Backend containerizado (Dockerfile) + variáveis de ambiente. `docker-compose.yml` sobe o backend
e permite servir o frontend estático. Compatível com qualquer ambiente cloud (Cloud Code, etc.).
