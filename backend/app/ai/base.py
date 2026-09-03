"""Interface abstrata de provedor de IA (ver docs/AI.md).

Nenhum código de negócio deve depender de um provedor específico — sempre
programe contra `AIProvider` e troque a implementação via `app/ai/router.py`.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class AIResult:
    text: str
    tokens_input: int
    tokens_output: int


class AIProvider(Protocol):
    name: str
    model: str

    def generate(self, prompt: str, *, max_tokens: int = 1024) -> AIResult: ...

    def classify(self, text: str, labels: list[str]) -> AIResult: ...

    def extract(self, text: str, schema_description: str) -> AIResult: ...

    def summarize(self, text: str) -> AIResult: ...
