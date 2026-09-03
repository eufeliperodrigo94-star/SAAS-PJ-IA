from types import SimpleNamespace

import pytest

from app.ai.base import AIResult
from app.ai.router import AIRouter, AIUnavailableError


class FakeSettings:
    anthropic_api_key = "fake-key"
    ai_default_model = "fake-model"


class FakeProvider:
    name = "fake"
    model = "fake-model"

    def __init__(self, result: AIResult | None = None, error: Exception | None = None):
        self._result = result
        self._error = error

    def extract(self, text, schema_description):
        if self._error:
            raise self._error
        return self._result


def test_extract_raises_when_no_api_key(monkeypatch):
    monkeypatch.setattr(
        "app.ai.router.get_settings", lambda: SimpleNamespace(anthropic_api_key="", ai_default_model="x")
    )
    recorded = {}
    monkeypatch.setattr(
        "app.repositories.ai_usage_repo.record_usage",
        lambda *a, **k: recorded.update(k, success=k.get("success")),
    )

    router = AIRouter()
    with pytest.raises(AIUnavailableError):
        router.extract(task="t", text="oi", schema_description="{}", organization_id="org-1")


def test_extract_returns_provider_text_and_records_usage(monkeypatch):
    monkeypatch.setattr("app.ai.router.get_settings", lambda: FakeSettings())
    fake_result = AIResult(text='{"ok": true}', tokens_input=10, tokens_output=5)
    monkeypatch.setattr(
        "app.ai.router.ClaudeProvider", lambda api_key, model: FakeProvider(result=fake_result)
    )

    recorded = {}
    monkeypatch.setattr(
        "app.repositories.ai_usage_repo.record_usage",
        lambda org_id, task, provider, model, **kwargs: recorded.update(
            org_id=org_id, task=task, provider=provider, model=model, **kwargs
        ),
    )

    router = AIRouter()
    text = router.extract(task="doc_extract", text="oi", schema_description="{}", organization_id="org-1")

    assert text == '{"ok": true}'
    assert recorded["success"] is True
    assert recorded["tokens_input"] == 10


def test_extract_wraps_provider_error(monkeypatch):
    monkeypatch.setattr("app.ai.router.get_settings", lambda: FakeSettings())
    monkeypatch.setattr(
        "app.ai.router.ClaudeProvider",
        lambda api_key, model: FakeProvider(error=RuntimeError("timeout")),
    )

    recorded = {}
    monkeypatch.setattr(
        "app.repositories.ai_usage_repo.record_usage",
        lambda org_id, task, provider, model, **kwargs: recorded.update(success=kwargs.get("success")),
    )

    router = AIRouter()
    with pytest.raises(AIUnavailableError):
        router.extract(task="doc_extract", text="oi", schema_description="{}", organization_id="org-1")

    assert recorded["success"] is False
