// Website editor sign-in: POST /api/cms/login  { username, password }
// Max 5 attempts per minute from one IP address (Netlify rate limit) plus a delay after each wrong attempt.
import { configured, checkLogin, makeSession, json } from "../lib/cms-auth.mjs";

export const config = {
  path: "/api/cms/login",
  rateLimit: { windowLimit: 5, windowSize: 60, aggregateBy: ["ip", "domain"] },
};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export default async (req) => {
  if (req.method !== "POST") return json({ ok: false, error: "method_not_allowed" }, 405);
  if (!configured()) return json({ ok: false, error: "not_configured" }, 503);
  const origin = req.headers.get("origin");
  if (origin && new URL(origin).host !== new URL(req.url).host) return json({ ok: false, error: "forbidden" }, 403);
  let body;
  try {
    const raw = await req.text();
    if (raw.length > 2000) return json({ ok: false, error: "too_large" }, 413);
    body = JSON.parse(raw);
  } catch {
    return json({ ok: false, error: "bad_request" }, 400);
  }
  const username = String(body.username || "").slice(0, 100);
  const password = String(body.password || "").slice(0, 200);
  if (!username || !password || !(await checkLogin(username, password))) {
    await sleep(800);
    return json({ ok: false, error: "invalid_login" }, 401);
  }
  const s = makeSession(username.trim());
  return json({ ok: true, token: s.token, exp: s.exp, name: username.trim() });
};
