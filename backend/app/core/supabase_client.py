from functools import lru_cache

from supabase import Client, create_client

from app.core.config import get_settings


@lru_cache
def get_supabase_admin() -> Client:
    """Client with the service_role key — server-side only, bypasses RLS.

    Use for administrative operations (e.g. creating an organization on
    registration). Never expose this key to the frontend.
    """
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
