"""AI Router (ver docs/AI.md): ponto único de acesso a provedores de IA.

Escolhe o provider/modelo por tarefa (hoje: Claude, modelo único configurável
por ambiente — nunca fixado na lógica de negócio) e registra toda chamada em
`ai_usage` (provider, modelo, tokens, latência, sucesso/erro). Erros do
provider nunca vazam para o cliente: viram `AIUnavailableError` com uma
mensagem genérica, com o motivo real preservado apenas no log de uso.
"""

import time

from app.ai.base import AIProvider, AIResult
from app.ai.providers.claude_provider import ClaudeProvider
from app.core.config import get_settings
from app.core.exceptions import DomainError
from app.repositories import ai_usage_repo


class AIUnavailableError(DomainError):
    def __init__(self, message: str = "Serviço de IA indisponível no momento.") -> None:
        super().__init__(message, status_code=503)


class AIRouter:
    def __init__(self) -> None:
        self._provider: AIProvider | None = None

    def _provider_instance(self) -> AIProvider:
        if self._provider is None:
            settings = get_settings()
            if not settings.anthropic_api_key:
                raise AIUnavailableError("IA não configurada (ANTHROPIC_API_KEY ausente).")
            self._provider = ClaudeProvider(settings.anthropic_api_key, settings.ai_default_model)
        return self._provider

    def _call(
        self,
        task: str,
        fn_name: str,
        args: tuple,
        *,
        organization_id: str,
        process_id: str | None = None,
        user_id: str | None = None,
    ) -> str:
        settings = get_settings()
        start = time.monotonic()

        try:
            provider = self._provider_instance()
        except AIUnavailableError as exc:
            ai_usage_repo.record_usage(
                organization_id,
                task,
                "claude",
                settings.ai_default_model,
                success=False,
                error_message=str(exc),
                process_id=process_id,
                user_id=user_id,
            )
            raise

        try:
            result: AIResult = getattr(provider, fn_name)(*args)
        except Exception as exc:
            ai_usage_repo.record_usage(
                organization_id,
                task,
                provider.name,
                provider.model,
                latency_ms=int((time.monotonic() - start) * 1000),
                success=False,
                error_message=str(exc),
                process_id=process_id,
                user_id=user_id,
            )
            raise AIUnavailableError() from exc

        ai_usage_repo.record_usage(
            organization_id,
            task,
            provider.name,
            provider.model,
            tokens_input=result.tokens_input,
            tokens_output=result.tokens_output,
            latency_ms=int((time.monotonic() - start) * 1000),
            success=True,
            process_id=process_id,
            user_id=user_id,
        )
        return result.text

    def extract(
        self,
        *,
        task: str,
        text: str,
        schema_description: str,
        organization_id: str,
        process_id: str | None = None,
        user_id: str | None = None,
    ) -> str:
        return self._call(
            task,
            "extract",
            (text, schema_description),
            organization_id=organization_id,
            process_id=process_id,
            user_id=user_id,
        )

    def summarize(
        self,
        *,
        task: str,
        text: str,
        organization_id: str,
        process_id: str | None = None,
        user_id: str | None = None,
    ) -> str:
        return self._call(
            task,
            "summarize",
            (text,),
            organization_id=organization_id,
            process_id=process_id,
            user_id=user_id,
        )


def get_ai_router() -> AIRouter:
    return AIRouter()
