from app.repositories import company_events_repo, processes_repo, validations_repo
from app.rules.engine import evaluate_process
from app.services.process_service import get_process_or_404


def _status_from_results(results: list[dict]) -> str:
    if any(r["result"] == "erro" for r in results):
        return "pendente_correcao"
    if results:
        return "pronto_para_protocolo"
    return "em_validacao"


def run_validation(organization_id: str, process_id: str, created_by: str | None = None) -> dict:
    process = get_process_or_404(organization_id, process_id)

    results = evaluate_process(organization_id, process)
    saved = validations_repo.replace_validations(organization_id, process_id, results)

    new_status = _status_from_results(results)
    updated_process = processes_repo.update_status(organization_id, process_id, new_status)

    errors = sum(1 for r in results if r["result"] == "erro")
    warnings = sum(1 for r in results if r["result"] == "atencao")
    company_events_repo.create_event(
        organization_id,
        process["company_id"],
        event_type="process.validated",
        description=f"Pré-validação executada: {errors} erro(s), {warnings} alerta(s).",
        payload={"errors": errors, "warnings": warnings, "total_rules": len(results)},
        process_id=process_id,
        created_by=created_by,
    )

    return {"process": updated_process, "validations": saved}


def list_validations(organization_id: str, process_id: str) -> list[dict]:
    get_process_or_404(organization_id, process_id)
    return validations_repo.list_validations(organization_id, process_id)
