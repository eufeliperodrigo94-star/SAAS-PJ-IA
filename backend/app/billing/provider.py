"""Interface de billing (ver docs/PROJECT.md, seção Assinaturas).

Nenhuma lógica de negócio deve depender de um gateway de pagamento
específico — sempre programe contra `BillingProvider`. O MVP não integra
nenhum gateway real ainda (`NullBillingProvider`); trocar de provider é
implementar esta interface e apontar `get_billing_provider` para ela.
"""

from typing import Protocol


class BillingProvider(Protocol):
    def create_checkout_session(self, organization_id: str, plan_code: str) -> dict:
        """Inicia uma cobrança externa para migrar a organização para `plan_code`."""
        ...

    def handle_webhook(self, payload: bytes, signature: str | None) -> dict:
        """Processa um evento assíncrono do gateway (pagamento confirmado, cancelado etc.)."""
        ...


class NullBillingProvider:
    """Provider padrão: nenhum gateway configurado. Troca de plano é feita
    diretamente (ver `billing_service.change_plan`), sem cobrança real."""

    def create_checkout_session(self, organization_id: str, plan_code: str) -> dict:
        raise NotImplementedError(
            "Nenhum gateway de pagamento configurado. Implemente BillingProvider "
            "e configure-o em get_billing_provider() para habilitar cobrança real."
        )

    def handle_webhook(self, payload: bytes, signature: str | None) -> dict:
        raise NotImplementedError("Nenhum gateway de pagamento configurado.")


def get_billing_provider() -> BillingProvider:
    return NullBillingProvider()
