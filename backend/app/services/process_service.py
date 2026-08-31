from app.core.exceptions import DomainError
from app.repositories import processes_repo
from app.services.company_service import get_company_or_404


class ProcessNotFoundError(DomainError):
    def __init__(self) -> None:
        super().__init__("Processo não encontrado.", status_code=404)


def list_processes(organization_id: str, company_id: str | None = None) -> list[dict]:
    return processes_repo.list_processes(organization_id, company_id)


def get_process_or_404(organization_id: str, process_id: str) -> dict:
    process = processes_repo.get_process(organization_id, process_id)
    if not process:
        raise ProcessNotFoundError()
    return process


def create_process(organization_id: str, created_by: str, data: dict) -> dict:
    # Garante que a empresa existe e pertence à mesma organização antes de criar o processo.
    get_company_or_404(organization_id, data["company_id"])
    return processes_repo.create_process(organization_id, created_by, data)
