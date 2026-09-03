# AI.md

## AI Router (implementado no Dia 5: `app/ai/`)

```python
class AIProvider(Protocol):
    def generate(self, prompt: str, *, max_tokens: int = 1024) -> AIResult: ...
    def classify(self, text: str, labels: list[str]) -> AIResult: ...
    def extract(self, text: str, schema_description: str) -> AIResult: ...
    def summarize(self, text: str) -> AIResult: ...
```

`app/ai/router.py` (`AIRouter`, use via `get_ai_router()`) é o único ponto de acesso a IA no
backend — nenhum serviço deve importar `anthropic` diretamente. O router:

- Instancia o provider (hoje: `ClaudeProvider`, `ANTHROPIC_API_KEY` + `AI_DEFAULT_MODEL` — nunca
  hard-coded no código de negócio).
- Mede latência e registra toda chamada em `ai_usage` (organização, processo, usuário, tarefa,
  provider, modelo, tokens de entrada/saída, sucesso/erro).
- Nunca deixa uma exceção do provider vazar para o cliente: qualquer falha (timeout, chave
  ausente, erro da API) vira `AIUnavailableError` (503) com mensagem genérica — o motivo real
  fica só no `ai_usage.error_message`.

## Usos implementados

- **Extração de documentos** (`app/services/document_service.py`): recebe o texto de um
  documento (ex.: contrato social colado pelo usuário — sem OCR automático no MVP), pede à IA
  um JSON estruturado e cruza com o cadastro da empresa via
  `app/documents/cross_check.py` (puramente determinístico, sem IA).
- **Assistente** (`app/services/assistant_service.py`): transforma uma frase em linguagem
  natural (ex.: "Quero retirar João e colocar Maria com 30%.") numa proposta JSON conforme o
  tipo do processo. **Nunca aplica a alteração sozinho** — a resposta só vira dado real quando o
  usuário confirma e usa os endpoints normais de sócios/endereços/CNAEs.

## Regra de ouro

Nunca enviar o histórico inteiro da empresa para a LLM. Buscar primeiro dados estruturados e
regras relevantes (camadas 1–4 de memória); só então chamar a IA (camada 5), e apenas quando
houver necessidade real de interpretação, extração, resumo ou explicação.

## Nunca

- IA não decide sozinha regras críticas nem altera dados sem confirmação explícita do usuário.
- IA nunca é apresentada como decisão oficial de órgão público.
- Sistema não deve depender de um único provedor de IA — trocar de provider é implementar
  `AIProvider` de novo e apontar `AIRouter._provider_instance` para ele.
