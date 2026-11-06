# Finlume website

Website for **Finlume Business Solutions (Pty) Ltd** — *Clarity in every number*.

Every page is **one complete file**: styles, scripts, fonts and logo are built into the HTML. There are **no folders**, so nothing can go missing when uploading.

## Files

| File | What it is |
|---|---|
| `index.html` | Home |
| `services.html` | Services |
| `about.html` | About Us |
| `contact.html` | Contact Us (form + WhatsApp) |
| `privacy.html` | POPIA Privacy Notice (includes the cookie section) |
| `terms.html` | Terms & Conditions |
| `thank-you.html` | Shown after the contact form is sent |
| `404.html` | Custom "page not found" |
| `Finlume-Company-Profile.pdf` | Downloadable company profile (compressed to ~0.5 MB) |
| `og-image.jpg` | Picture shown when the site is shared on WhatsApp, LinkedIn, Facebook |
| `favicon.ico`, `favicon-32.png`, `apple-touch-icon.png` | Browser-tab and phone icons |
| `profile-cover.jpg` | Company profile cover shown on the Home page |
| `netlify.toml` | Netlify settings: security headers, short URLs, rate limits, blocked hacking paths |
| `sitemap.xml`, `robots.txt`, `security.txt` | For search engines and security researchers |

## Upload to GitHub → Netlify

1. In the GitHub repository, delete the old website files.
2. **Add file → Upload files** → select **all the files** in this folder → **Commit changes**.
3. Netlify publishes automatically (Build command: empty, Publish directory: `.`).
4. In Netlify: **Domain management → HTTPS** — make sure the certificate is active. Netlify then automatically redirects every `http://` visit to `https://` (forced HTTPS), and the site also sends a 2-year HSTS header so browsers always use HTTPS.
5. Contact form: messages are emailed to rochelle@finlume.co.za by **FormSubmit** (built into the page code, no Netlify setting needed). The very first message triggers a one-time **activation email** from FormSubmit to rochelle@ — click **Activate Form** in it. FormSubmit then also sends a random alias; you can put it in `content.py` (`FORM_TO`) and rebuild to hide the email address from the page code.

## What's built in

**Pages & SEO:** unique meta title and description on every page, social sharing image and tags (Open Graph + Twitter/X), favicon, sitemap with dates, robots.txt, canonical URLs, short addresses (`/about`, `/services`, `/contact`, `/privacy`, `/terms`, `/profile`).

**Quality (tested):** Lighthouse scores of 97–98 for Performance and 100 for Accessibility, Best Practices and SEO; zero automated accessibility errors on every page (including colour contrast); mobile layout checked at phone width with no sideways scrolling; no broken links; every image has alt text; fonts trimmed to the characters used.

**One clear call to action:** every primary button says *Book a free consultation* and goes to the Contact page.

**Cookie notice:** the site uses no advertising or tracking cookies. The notice explains this and remembers the visitor's choice on their device.

**Contact form:** checks every field (required fields, real email format, phone format, minimum lengths, POPIA consent) before sending. Spam protection: a hidden honeypot field (FormSubmit `_honey`), a block on instant "bot-speed" submissions, a 60-second pause between submissions, and a Netlify rate limit on the contact page.

**Security:**
- No secrets, passwords or API keys in the website code (checked).
- Strict Content-Security-Policy: each page only runs its own fingerprinted code; injected scripts are blocked (tested).
- Cannot be embedded in other websites (anti-clickjacking), `nosniff`, strict referrer and permissions policies.
- Rate limiting (Netlify, available on all plans): `/services` max 60 and `/contact` max 30 requests per minute per IP address.
- Common hacking paths (`/wp-admin`, `/.env`, `/.git`, `/admin`, `/phpmyadmin` …) return 404.

**About passwords:** this website has **no logins and stores no passwords**, so there is nothing to hash or brute-force — that is the most secure setup. If a client portal or login is ever added, use a managed service (for example Netlify Identity's replacement or Auth0/Clerk) which provides bcrypt/Argon2 password hashing, login rate limiting and 2-factor login out of the box — never store passwords in the website files.

Protect the accounts too: turn on **two-factor login** for GitHub, Netlify, HostAfrica and the rochelle@ mailbox.

## Before going fully live — please complete

- **Terms page (ECT Act, section 43):** add the company registration number and physical address in `content.py` (`REG_NO`, `PHYSICAL_ADDRESS`) and rebuild — they then appear automatically.
- Have the Privacy Notice and Terms & Conditions reviewed by your legal adviser.
- Replace the "RB" placeholder with Rochelle's photo when available.

## Editing later

Pages are generated from `content.py` by `build.py` (kept in the project, not uploaded). For a small text change you can edit an HTML file directly, but don't change anything inside the `<style>` or `<script>` blocks — the security policy checks their exact contents.
