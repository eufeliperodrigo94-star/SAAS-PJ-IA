# AI.md

## AI Router

Interface abstrata (implementação a partir do Dia 5):

```python
class AIProvider(Protocol):
    def generate(self, prompt: str, **kwargs) -> str: ...
    def classify(self, text: str, labels: list[str], **kwargs) -> str: ...
    def extract(self, text: str, schema: dict, **kwargs) -> dict: ...
    def summarize(self, text: str, **kwargs) -> str: ...
```

Provider padrão: Claude (`ANTHROPIC_API_KEY`, modelo configurável via env, nunca hard-coded).
O router escolhe modelo por tarefa/custo/complexidade e registra provider, modelo, tokens,
latência, custo estimado, processo e usuário (tabela `ai_usage`).

## Regra de ouro

Nunca enviar o histórico inteiro da empresa para a LLM. Buscar primeiro dados estruturados e
regras relevantes (camadas 1–4 de memória); só então chamar a IA (camada 5), e apenas quando
houver necessidade real de interpretação, extração, resumo ou explicação.

## Nunca

- IA não decide sozinha regras críticas nem altera dados sem confirmação explícita do usuário.
- IA nunca é apresentada como decisão oficial de órgão público.
- Sistema não deve depender de um único provedor de IA.
