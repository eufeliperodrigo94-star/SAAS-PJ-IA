import pytest

from app.core.exceptions import DomainError
from app.services import assistant_service


class FakeRouter:
    def __init__(self, raw: str):
        self.raw = raw

    def extract(self, **kwargs):
        return self.raw


def _patch_process(monkeypatch, process_type: str):
    monkeypatch.setattr(
        "app.services.assistant_service.get_process_or_404",
        lambda org_id, process_id: {"id": process_id, "company_id": "c1", "type": process_type},
    )
    monkeypatch.setattr(
        "app.repositories.company_events_repo.create_event", lambda *a, **k: {"id": "event-1"}
    )


def test_interpret_message_never_applies_automatically(monkeypatch):
    _patch_process(monkeypatch, "alteracao_qsa")
    raw = '{"acao": "retirar_socio", "socio_alvo": "João", "novo_socio": {"nome": "Maria", "percentual_capital": 30}, "novo_percentual": null}'
    monkeypatch.setattr("app.services.assistant_service.get_ai_router", lambda: FakeRouter(raw))

    result = assistant_service.interpret_message("org-1", "p1", "Quero retirar João e colocar Maria com 30%.", "user-1")

    assert result["requires_confirmation"] is True
    assert result["proposal"]["acao"] == "retirar_socio"
    assert result["proposal"]["novo_socio"]["nome"] == "Maria"


def test_interpret_message_uses_default_schema_for_unmapped_process_type(monkeypatch):
    _patch_process(monkeypatch, "abertura")
    captured = {}

    class CapturingRouter(FakeRouter):
        def extract(self, **kwargs):
            captured.update(kwargs)
            return self.raw

    monkeypatch.setattr(
        "app.services.assistant_service.get_ai_router",
        lambda: CapturingRouter('{"resumo": "abertura de empresa", "campos_identificados": {}}'),
    )

    assistant_service.interpret_message("org-1", "p1", "Quero abrir uma empresa.", "user-1")

    assert captured["schema_description"] == assistant_service.DEFAULT_SCHEMA


def test_interpret_message_invalid_json_raises(monkeypatch):
    _patch_process(monkeypatch, "alteracao_qsa")
    monkeypatch.setattr(
        "app.services.assistant_service.get_ai_router", lambda: FakeRouter("não é json")
    )

    with pytest.raises(DomainError):
        assistant_service.interpret_message("org-1", "p1", "mensagem", "user-1")
