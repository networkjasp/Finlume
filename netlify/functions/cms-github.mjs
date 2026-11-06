// Website editor relay: /api/gh/*  →  https://api.github.com/*
// The editor never sees the GitHub token. It only holds a short-lived signed session from cms-login,
// and only the GitHub requests the editor needs (reading and saving files in this repository) are passed on.
import { configured, readSession, githubToken, json } from "../lib/cms-auth.mjs";

export const config = {
  path: "/api/gh/*",
  rateLimit: { windowLimit: 300, windowSize: 60, aggregateBy: ["ip", "domain"] },
};

const GITHUB = process.env.GITHUB_API_URL || "https://api.github.com";
const ALLOWED = [
  /^\/user$/,
  /^\/repos\/[\w.-]+\/[\w.-]+$/,
  /^\/repos\/[\w.-]+\/[\w.-]+\/(branches|commits|compare|contents)(\/.*)?$/,
  /^\/repos\/[\w.-]+\/[\w.-]+\/git\/(blobs|commits|refs|trees)(\/.*)?$/,
];
const METHODS = new Set(["GET", "HEAD", "POST", "PATCH", "PUT"]);

export default async (req) => {
  if (!configured()) return json({ message: "Website editor is not set up yet" }, 503);
  const auth = req.headers.get("authorization") || "";
  const session = readSession(auth.replace(/^(token|bearer)\s+/i, ""));
  if (!session) return json({ message: "Bad credentials" }, 401);

  const url = new URL(req.url);
  const path = url.pathname.replace(/^\/api\/gh/, "") || "/";
  if (!METHODS.has(req.method) || !ALLOWED.some((r) => r.test(path)) || path.includes(".."))
    return json({ message: "Not allowed" }, 403);

  const headers = {
    Authorization: "Bearer " + githubToken(),
    Accept: req.headers.get("accept") || "application/vnd.github+json",
    "User-Agent": "finlume-website-editor",
    "X-GitHub-Api-Version": "2022-11-28",
  };
  const init = { method: req.method, headers };
  if (!["GET", "HEAD"].includes(req.method)) {
    headers["Content-Type"] = req.headers.get("content-type") || "application/json";
    init.body = await req.arrayBuffer();
  }
  let res;
  try {
    res = await fetch(GITHUB + path + url.search, init);
  } catch {
    return json({ message: "GitHub could not be reached" }, 502);
  }
  const out = new Headers({ "Cache-Control": "no-store", "X-Robots-Tag": "noindex" });
  for (const h of ["content-type", "etag", "link", "last-modified"]) {
    const v = res.headers.get(h);
    if (v) out.set(h, v);
  }
  return new Response(req.method === "HEAD" ? null : await res.arrayBuffer(), { status: res.status, headers: out });
};
