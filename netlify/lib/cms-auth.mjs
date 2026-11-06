// Shared by the website editor's login and GitHub relay functions.
// Nothing secret is stored in this file: the settings come from Netlify environment variables.
//   CMS_USERNAME       the editor username (for example Admin)
//   CMS_PASSWORD_HASH  scrypt hash of the editor password (never the password itself)
//   GITHUB_TOKEN       fine-grained GitHub token limited to this website's repository
import { createHmac, createHash, scrypt, timingSafeEqual } from "node:crypto";

export const SESSION_HOURS = 8;

const env = (k) => (process.env[k] || "").trim();

export function configured() {
  return !!(env("CMS_USERNAME") && env("CMS_PASSWORD_HASH") && env("GITHUB_TOKEN"));
}

export function githubToken() {
  return env("GITHUB_TOKEN");
}

function key() {
  // Changing the password or the GitHub token signs everyone out.
  return createHash("sha256").update("finlume-cms-v1|" + env("GITHUB_TOKEN") + "|" + env("CMS_PASSWORD_HASH")).digest();
}

const b64u = (buf) => Buffer.from(buf).toString("base64url");

function same(a, b) {
  const x = Buffer.from(String(a)), y = Buffer.from(String(b));
  return x.length === y.length && timingSafeEqual(x, y);
}

export async function checkLogin(username, password) {
  const [algo, N, r, p, salt, hash] = env("CMS_PASSWORD_HASH").split(":");
  if (algo !== "scrypt" || !salt || !hash) return false;
  const want = Buffer.from(hash, "base64");
  const got = await new Promise((res, rej) =>
    scrypt(String(password).normalize("NFC"), Buffer.from(salt, "base64"), want.length,
      { N: +N, r: +r, p: +p, maxmem: 64 * 1024 * 1024 }, (e, k) => (e ? rej(e) : res(k))));
  const passOk = got.length === want.length && timingSafeEqual(got, want);
  const userOk = same(String(username).trim().toLowerCase(), env("CMS_USERNAME").toLowerCase());
  return passOk && userOk;
}

export function makeSession(username) {
  const exp = Date.now() + SESSION_HOURS * 3600 * 1000;
  const body = b64u(JSON.stringify({ u: username, exp }));
  const sig = b64u(createHmac("sha256", key()).update(body).digest());
  return { token: body + "." + sig, exp };
}

export function readSession(token) {
  const [body, sig] = String(token || "").split(".");
  if (!body || !sig) return null;
  const want = b64u(createHmac("sha256", key()).update(body).digest());
  if (!same(sig, want)) return null;
  try {
    const data = JSON.parse(Buffer.from(body, "base64url").toString());
    return data.exp > Date.now() ? data : null;
  } catch {
    return null;
  }
}

export function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store", "X-Robots-Tag": "noindex" },
  });
}
