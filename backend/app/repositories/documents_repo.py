import re
import uuid
from datetime import datetime, timezone

from app.core.supabase_client import get_supabase_admin

BUCKET = "documents"

# Mantém apenas caracteres seguros para uma chave de Storage — sem barras,
# nem sequências "..", removendo qualquer risco de o nome de arquivo
# escapar da pasta "{organization_id}/{process_id}/" do objeto.
_UNSAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9._-]+")


def _sanitize_filename(filename: str) -> str:
    name = filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    name = _UNSAFE_FILENAME_CHARS.sub("_", name).lstrip(".") or "arquivo"
    return name[:200]


def upload_file(organization_id: str, process_id: str, filename: str, content: bytes, content_type: str | None) -> str:
    safe_filename = _sanitize_filename(filename)
    storage_path = f"{organization_id}/{process_id}/{uuid.uuid4()}_{safe_filename}"
    get_supabase_admin().storage.from_(BUCKET).upload(
        storage_path,
        content,
        {"content-type": content_type or "application/octet-stream"},
    )
    return storage_path


def create_document(organization_id: str, process_id: str, data: dict) -> dict:
    payload = {**data, "organization_id": organization_id, "process_id": process_id}
    result = get_supabase_admin().table("documents").insert(payload).execute()
    return result.data[0]


def list_documents(organization_id: str, process_id: str) -> list[dict]:
    result = (
        get_supabase_admin()
        .table("documents")
        .select("*")
        .eq("organization_id", organization_id)
        .eq("process_id", process_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


def get_document(organization_id: str, document_id: str) -> dict | None:
    result = (
        get_supabase_admin()
        .table("documents")
        .select("*")
        .eq("organization_id", organization_id)
        .eq("id", document_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def save_extraction(organization_id: str, document_id: str, extracted_data: dict) -> dict:
    result = (
        get_supabase_admin()
        .table("documents")
        .update(
            {
                "extracted_data": extracted_data,
                "extracted_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        .eq("organization_id", organization_id)
        .eq("id", document_id)
        .execute()
    )
    return result.data[0]
