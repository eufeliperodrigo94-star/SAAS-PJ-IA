from datetime import datetime, timedelta, timezone

from app.repositories import ai_usage_repo, companies_repo, processes_repo, validations_repo
from app.services import billing_service

IN_PROGRESS_STATUSES = ["rascunho", "em_validacao"]
PENDING_CORRECTION_STATUSES = ["pendente_correcao"]
READY_STATUSES = ["pronto_para_protocolo"]


def get_summary(organization_id: str) -> dict:
    subscription = billing_service.get_current_subscription(organization_id)
    since = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

    return {
        "organization_id": organization_id,
        "total_companies": companies_repo.count_companies(organization_id),
        "processes_in_progress": processes_repo.count_by_status(
            organization_id, IN_PROGRESS_STATUSES
        ),
        "pending_issues": processes_repo.count_by_status(
            organization_id, PENDING_CORRECTION_STATUSES
        ),
        "errors": validations_repo.count_by_result(organization_id, "erro"),
        "alerts": validations_repo.count_by_result(organization_id, "atencao"),
        "ready_for_filing": processes_repo.count_by_status(organization_id, READY_STATUSES),
        "ai_usage_last_30_days": ai_usage_repo.summary_since(organization_id, since),
        "current_plan": subscription["plan"] if subscription else None,
    }
