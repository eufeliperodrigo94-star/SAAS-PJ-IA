// Cliente Supabase (auth) + helper de API para o backend FastAPI.
// Carregado após config.js e o script da Supabase JS (CDN) em cada página.

const supabaseClient = window.supabase.createClient(
  window.APP_CONFIG.SUPABASE_URL,
  window.APP_CONFIG.SUPABASE_ANON_KEY
);

async function getAccessToken() {
  const { data } = await supabaseClient.auth.getSession();
  return data.session ? data.session.access_token : null;
}

async function apiFetch(path, options = {}) {
  const token = await getAccessToken();
  const isFormData = options.body instanceof FormData;
  const headers = {
    ...(isFormData ? {} : { "Content-Type": "application/json" }),
    ...(options.headers || {}),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${window.APP_CONFIG.API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch (_) {
      // ignore JSON parse errors on error responses
    }
    throw new Error(detail);
  }

  return response.status === 204 ? null : response.json();
}

async function requireSession(redirectTo = "login.html") {
  const { data } = await supabaseClient.auth.getSession();
  if (!data.session) {
    window.location.href = redirectTo;
    return null;
  }
  return data.session;
}

async function signOut() {
  await supabaseClient.auth.signOut();
  window.location.href = "login.html";
}

async function showAdminNavIfSuperAdmin() {
  const navAdmin = document.getElementById("nav-admin");
  if (!navAdmin) return;
  try {
    const me = await apiFetch("/auth/me");
    navAdmin.style.display = me.is_super_admin ? "" : "none";
  } catch (_) {
    // sessão ainda carregando ou erro de rede — mantém o link oculto.
  }
}
