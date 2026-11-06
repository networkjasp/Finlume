// Contact form -> email, built into the website (Netlify Function, free plan).
// Reusable on any website: copy this file to netlify/functions/contact.mjs and set, in
// Netlify -> Site configuration -> Environment variables (secrets never go in this file):
//   SMTP_USER   the mailbox that sends, e.g. rochelle@finlume.co.za
//   SMTP_PASS   that mailbox's password
//   MAIL_TO     where enquiries go, e.g. info@finlume.co.za   (default: SMTP_USER)
//   SMTP_HOST   optional, default mail.<domain of SMTP_USER>   (cPanel hosting standard)
//   SMTP_PORT   optional, default 465 (SSL)
//   FORM_SITE_NAME   optional, shown in the email subject, e.g. Finlume
// The form only accepts messages sent from the website itself (same domain) or ALLOWED_ORIGINS.
import tls from "node:tls";
import crypto from "node:crypto";

export const config = {
  path: "/api/contact",
  // Netlify rate limit (all plans): max 5 submissions per minute from one IP address
  rateLimit: { windowLimit: 5, windowSize: 60, aggregateBy: ["ip", "domain"] },
};

const MAX = { name: 100, email: 150, phone: 25, company: 120, service: 80, message: 3000 };
// Same website only (www and non-www), plus any extra addresses in ALLOWED_ORIGINS (comma list)
const originAllowed = (origin, reqUrl) => {
  const self = new URL(reqUrl).hostname.replace(/^www\./, "");
  let host;
  try { host = new URL(origin).hostname.replace(/^www\./, ""); } catch { return false; }
  if (host === self) return true;
  return String(env("ALLOWED_ORIGINS", "")).split(",").map((x) => x.trim()).filter(Boolean).includes(origin);
};

const env = (k, d) => (globalThis.Netlify?.env?.get(k) ?? process.env[k] ?? d);
const json = (status, body) => new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
const clean = (v, k) => {
  let s = String(v ?? "");
  s = k === "message" ? s.replace(/\r\n?/g, "\n") : s.replace(/[\r\n\t]+/g, " ");
  return s.replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "").trim().slice(0, MAX[k]);
};

export default async (req, context) => {
  if (req.method !== "POST") return new Response("Method not allowed", { status: 405, headers: { Allow: "POST" } });
  const origin = req.headers.get("origin");
  if (origin && !originAllowed(origin, req.url)) return json(403, { ok: false, error: "forbidden" });

  const type = req.headers.get("content-type") || "";
  const wantsHtml = !type.includes("application/json");
  let data;
  try {
    const raw = await req.text();
    if (raw.length > 20000) return json(413, { ok: false, error: "too large" });
    data = type.includes("application/json") ? JSON.parse(raw) : Object.fromEntries(new URLSearchParams(raw));
  } catch { return json(400, { ok: false, error: "bad request" }); }

  const thanks = () => (wantsHtml ? Response.redirect(new URL("/thank-you", req.url), 303) : json(200, { ok: true }));
  if (data["bot-field"]) return thanks(); // honeypot filled in: silently ignore bots

  const f = {};
  for (const k of Object.keys(MAX)) f[k] = clean(data[k], k);
  // Visitors may leave the message as it is: use a friendly default if it is empty
  if (!f.message) f.message = "Hi, please contact me to book a free consultation." + (f.service ? " I'm interested in " + f.service + "." : "");
  const valid = f.name.length >= 2 && /^[^\s@<>"]+@[^\s@<>"]+\.[a-z]{2,}$/i.test(f.email) && f.message.length >= 10 && data.consent === "Yes";
  if (!valid) return json(422, { ok: false, error: "invalid" });

  const user = env("SMTP_USER"), pass = env("SMTP_PASS");
  if (!user || !pass) { console.error("contact: SMTP_USER/SMTP_PASS not set"); return json(503, { ok: false, error: "not configured" }); }

  const siteName = env("FORM_SITE_NAME", new URL(req.url).hostname.replace(/^www\./, ""));
  const text = [
    "New enquiry from the " + siteName + " website", "",
    "Name:     " + f.name, "Email:    " + f.email, "Phone:    " + (f.phone || "-"),
    "Company:  " + (f.company || "-"), "Service:  " + (f.service || "-"), "", "Message:", f.message, "",
    "POPIA consent given: Yes", "Sent: " + new Date().toLocaleString("en-ZA", { timeZone: "Africa/Johannesburg" }),
    "", "Click Reply to answer " + f.name + " directly.",
  ].join("\n");

  const sending = sendMail({
      host: env("SMTP_HOST", "mail." + user.split("@")[1]), port: Number(env("SMTP_PORT", "465")), user, pass,
      from: user, to: env("MAIL_TO", user), siteName,
      replyName: f.name.replace(/["<>\\]/g, ""), replyTo: f.email,
      subject: siteName + " website enquiry from " + f.name + (f.service ? " (" + f.service + ")" : ""), text,
    }).then(() => ({ ok: true }), (e) => ({ ok: false, error: e.message }));

  // Wait up to 4 seconds for the mail server. Almost all failures (wrong password, server down)
  // happen within that time and are reported to the visitor. If the server is simply slow,
  // reply to the visitor straight away and let the email finish in the background.
  const first = await Promise.race([sending, new Promise((r) => setTimeout(() => r(null), 4000))]);
  if (first === null && context && typeof context.waitUntil === "function") {
    context.waitUntil(sending.then((r) => { if (!r.ok) console.error("contact: send failed (background):", r.error); }));
    return thanks();
  }
  const result = first || (await sending);
  if (!result.ok) {
    console.error("contact: send failed:", result.error);
    return json(502, { ok: false, error: "send failed" });
  }
  return thanks();
};

const b64 = (s) => Buffer.from(s, "utf8").toString("base64");
const encWord = (s) => (/^[\x20-\x7E]*$/.test(s) ? s : "=?UTF-8?B?" + b64(s) + "?=");

export function sendMail({ host, port, user, pass, from, to, siteName = "Website", replyName, replyTo, subject, text, rejectUnauthorized = true }) {
  return new Promise((resolve, reject) => {
    const sock = tls.connect({ host, port, servername: host, rejectUnauthorized });
    sock.setTimeout(15000, () => sock.destroy(new Error("SMTP timeout")));
    sock.setEncoding("utf8");
    let buf = "", lines = [], replies = [], waiters = [], failed = null;
    const fail = (e) => { if (failed) return; failed = e; waiters.splice(0).forEach((w) => w.reject(e)); reject(e); };
    sock.on("error", fail);
    sock.on("close", () => fail(new Error("SMTP connection closed")));
    sock.on("data", (d) => {
      buf += d;
      let i;
      while ((i = buf.indexOf("\n")) >= 0) {
        const line = buf.slice(0, i).replace(/\r$/, ""); buf = buf.slice(i + 1); lines.push(line);
        if (/^\d{3}(?: |$)/.test(line)) { const r = lines.join("\n"); lines = []; const w = waiters.shift(); w ? w.resolve(r) : replies.push(r); }
      }
    });
    const next = () => new Promise((res, rej) => { if (failed) return rej(failed); replies.length ? res(replies.shift()) : waiters.push({ resolve: res, reject: rej }); });
    const cmd = async (line, ok) => {
      if (line !== null) sock.write(line + "\r\n");
      const r = await next();
      if (!ok.includes(Number(r.slice(0, 3)))) throw new Error("SMTP " + r.slice(0, 160).replace(/\s+/g, " "));
      return r;
    };
    const domain = from.split("@")[1] || "localhost";
    const headers = [
      "From: " + encWord(siteName + " Website") + " <" + from + ">",
      "To: <" + to + ">",
      "Reply-To: " + (replyName ? '"' + encWord(replyName) + '" ' : "") + "<" + replyTo + ">",
      "Subject: " + encWord(subject),
      "Date: " + new Date().toUTCString().replace("GMT", "+0000"),
      "Message-ID: <" + crypto.randomUUID() + "@" + domain + ">",
      "MIME-Version: 1.0",
      "Content-Type: text/plain; charset=utf-8",
      "Content-Transfer-Encoding: base64",
      "Auto-Submitted: auto-generated",   // stops autoresponders replying to the website
      "X-Auto-Response-Suppress: All",
    ];
    const body = b64(text).replace(/.{1,76}/g, "$&\r\n");
    (async () => {
      await cmd(null, [220]);
      const ehlo = await cmd("EHLO " + domain, [250]);
      // Fewer round trips = faster sending (each one crosses the ocean to the mail server)
      if (/AUTH[^\n]*PLAIN/i.test(ehlo)) {
        await cmd("AUTH PLAIN " + Buffer.from("\0" + user + "\0" + pass, "utf8").toString("base64"), [235]);
      } else {
        await cmd("AUTH LOGIN", [334]); await cmd(b64(user), [334]); await cmd(b64(pass), [235]);
      }
      if (/PIPELINING/i.test(ehlo)) {
        sock.write("MAIL FROM:<" + from + ">\r\nRCPT TO:<" + to + ">\r\nDATA\r\n");
        await cmd(null, [250]); await cmd(null, [250, 251]); await cmd(null, [354]);
      } else {
        await cmd("MAIL FROM:<" + from + ">", [250]);
        await cmd("RCPT TO:<" + to + ">", [250, 251]);
        await cmd("DATA", [354]);
      }
      await cmd(headers.join("\r\n") + "\r\n\r\n" + body + ".", [250]);
      sock.removeAllListeners("close");
      try { sock.write("QUIT\r\n"); } catch {}
      sock.end();
      resolve();
    })().catch((e) => { sock.destroy(); fail(e); });
  });
}
