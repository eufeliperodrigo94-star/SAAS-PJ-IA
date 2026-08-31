import anthropic

from app.ai.base import AIResult


class ClaudeProvider:
    """Provider padrão do AI Router (ver docs/AI.md). Implementa `AIProvider`
    via duck typing — sem herdar de Protocol, para não acoplar a assinatura."""

    name = "claude"

    def __init__(self, api_key: str, model: str):
        self.model = model
        self._client = anthropic.Anthropic(api_key=api_key)

    def _complete(self, prompt: str, *, max_tokens: int) -> AIResult:
        response = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in response.content if block.type == "text")
        return AIResult(
            text=text,
            tokens_input=response.usage.input_tokens,
            tokens_output=response.usage.output_tokens,
        )

    def generate(self, prompt: str, *, max_tokens: int = 1024) -> AIResult:
        return self._complete(prompt, max_tokens=max_tokens)

    def classify(self, text: str, labels: list[str]) -> AIResult:
        prompt = (
            f"Classifique o texto abaixo em exatamente uma destas categorias: {', '.join(labels)}.\n"
            "Responda apenas com a categoria escolhida, sem explicações.\n\n"
            f"Texto:\n{text}"
        )
        return self._complete(prompt, max_tokens=32)

    def extract(self, text: str, schema_description: str) -> AIResult:
        prompt = (
            "Extraia as informações do texto abaixo e responda **apenas** com um JSON válido, "
            f"sem markdown, seguindo exatamente este formato: {schema_description}\n"
            "Se um campo não puder ser determinado com segurança, use null — nunca invente dados.\n\n"
            f"Texto:\n{text}"
        )
        return self._complete(prompt, max_tokens=1024)

    def summarize(self, text: str) -> AIResult:
        prompt = f"Resuma o texto abaixo em português, em até 5 frases:\n\n{text}"
        return self._complete(prompt, max_tokens=512)
