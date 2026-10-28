# Finlume website

Website for **Finlume Business Solutions (Pty) Ltd** — *Clarity in every number*.

## Why this version is easy to upload

Every page is **one complete file**. The styles, scripts, fonts and logo are built into each HTML file, so there are **no folders to upload** and nothing can go missing.

| File | What it is |
|---|---|
| `index.html` | Home |
| `services.html` | Services |
| `about.html` | About Us |
| `contact.html` | Contact Us (Netlify contact form + WhatsApp) |
| `privacy.html` | POPIA Privacy Notice |
| `thank-you.html` | Shown after the contact form is sent |
| `404.html` | "Page not found" |
| `Finlume-Company-Profile.pdf` | Downloadable company profile |
| `og-image.jpg`, `apple-touch-icon.png` | Social-sharing picture and phone icon |
| `netlify.toml` | Netlify settings: security headers, short URLs, blocked hacking paths |
| `robots.txt`, `sitemap.xml`, `security.txt` | For search engines and security researchers |

## Upload to GitHub → Netlify

1. In your GitHub repository, **delete the old website files first** (old `assets` folder, old pages, old `netlify.toml`).
2. **Add file → Upload files** → select **all the files** in this folder → **Commit changes**.
3. Netlify publishes automatically. Build command: *empty*. Publish directory: `.`
4. If Netlify says *"Unrecognized Git contributor"*: make the GitHub repository public (Settings → Change visibility), or connect the uploading GitHub account to your Netlify login. Then **Deploys → Trigger deploy → Deploy site**.

## Contact form

Netlify detects the form named **contact** automatically. See messages under **Netlify → Forms**. For email alerts: **Forms → Form notifications → Add notification → Email** → info@finlume.co.za.

## Security

- No logins, admin area, database or server code — nothing to break into.
- Strict Content-Security-Policy: only the code built into each page may run (verified by fingerprint), so injected scripts are blocked.
- Cannot be embedded in other sites (anti-clickjacking), HTTPS enforced, `nosniff`, strict referrer and permissions policies.
- Common hacking paths (`/wp-admin`, `/.env`, `/.git`, `/admin`, `/phpmyadmin` …) return 404.
- Contact form: hidden spam trap, Netlify spam filtering, length limits, required POPIA consent.

Protect the accounts too: turn on **two-factor login** for GitHub and Netlify, and switch on Netlify deploy email notifications.

## Editing later

The pages are generated from `content.py` by `build.py` (kept in the project). For a small text change you can also open the HTML file in a text editor, search for the sentence and edit it — just don't change anything inside the `<style>` or `<script>` blocks, because the security policy checks their exact contents.
