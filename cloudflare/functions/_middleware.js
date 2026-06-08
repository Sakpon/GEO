// Edge HTTP Basic Auth gate for the whole Pages project (the page + /api/*).
// Credentials come from environment variables, defaulting to thedent/admin2026.
// Set BASIC_AUTH_USERNAME / BASIC_AUTH_PASSWORD on the Pages project and change
// the password before going live.

function unauthorized() {
  return new Response("Authentication required.", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="The Dent AIO Audit"' },
  });
}

// Constant-time-ish string compare.
function safeEqual(a, b) {
  if (a.length !== b.length) return false;
  let out = 0;
  for (let i = 0; i < a.length; i++) out |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return out === 0;
}

export async function onRequest(context) {
  const { request, env, next } = context;
  const user = env.BASIC_AUTH_USERNAME || "thedent";
  const pass = env.BASIC_AUTH_PASSWORD || "admin2026";

  const header = request.headers.get("Authorization") || "";
  if (!header.startsWith("Basic ")) return unauthorized();

  let decoded = "";
  try {
    decoded = atob(header.slice(6));
  } catch {
    return unauthorized();
  }
  const idx = decoded.indexOf(":");
  const u = decoded.slice(0, idx);
  const p = decoded.slice(idx + 1);
  if (!safeEqual(u, user) || !safeEqual(p, pass)) return unauthorized();

  return next();
}
