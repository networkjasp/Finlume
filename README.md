# Finlume website

Website for **Finlume Business Solutions (Pty) Ltd**, *Clarity in every number*.

## How it works now

```
content/*.json  ──►  build.py (Netlify runs it)  ──►  dist/  (the live website)
      ▲
      └── edited in the Website editor at /studio/  (click the © symbol in the footer 5 times quickly)
```

All the text on the site lives in the `content` folder. The Website editor changes those files on GitHub, Netlify notices the change, rebuilds the pages and publishes them, usually within a minute or two.

## Files in this repository

| File or folder | What it is |
|---|---|
| `content/` | All editable text: `home.json`, `services.json`, `about.json`, `contact.json`, `settings.json` (phone, email, address) |
| `uploads/` | Pictures uploaded in the Website editor (for example Rochelle's photo) |
| `build.py`, `content.py` | Turn the text into finished pages. Netlify runs these automatically |
| `studio/` | The Website editor program (Decap CMS 3.17.1, stored here so no outside script is loaded) |
| `netlify/functions/contact.mjs` | Sends contact-form messages to info@finlume.co.za |
| `netlify.toml` | Netlify settings: build command, short addresses, security headers, rate limits |
| `fonts/`, images, `Finlume-Company-Profile.pdf` | Used to build the pages |

Do **not** upload any `.env` file. The mailbox password lives only in Netlify.

## 1. Upload to GitHub (replaces the old files)

1. Open the repository on GitHub. Delete the old website files (the old `.html` files and the old `netlify` folder).
2. **Add file → Upload files** → drag **everything** from this folder, including the folders `content`, `uploads`, `studio`, `fonts` and `netlify` → **Commit changes**.
3. Check the repo now shows `build.py`, `netlify.toml` and `content/home.json` at the top level.
4. Netlify builds the site by itself (the build settings are in `netlify.toml`). In Netlify → **Deploys**, the latest deploy should say **Published**.

## 2. Turn on the Website editor sign-in (once, about 5 minutes)

The editor signs in with GitHub. Only GitHub accounts that can change this repository can edit the site.

**A. Create a GitHub "OAuth App"**
1. Go to **github.com/settings/developers** → **OAuth Apps** → **New OAuth App**.
2. Fill in:
   - Application name: `Finlume website editor`
   - Homepage URL: `https://www.finlume.co.za`
   - Authorization callback URL: `https://api.netlify.com/auth/done`
3. Click **Register application**. Copy the **Client ID**. Click **Generate a new client secret** and copy it (it's shown only once).

**B. Give the keys to Netlify**
1. Netlify → your site → **Project configuration → Security → OAuth** (older screens: **Site configuration → Access & security → OAuth**).
2. Under **Authentication providers** click **Install provider** → **GitHub** → paste the Client ID and Client secret → **Install**.

**C. Try it**
1. Open www.finlume.co.za, scroll to the footer and click the **©** symbol **5 times quickly**.
2. Click **Login with GitHub** → **Authorize**.
3. Open **Website → About page**, change something, click **Publish → Publish now**. Refresh the live site after a minute or two.

## Using the editor

- **Website → Home page / Services page / About page / Contact page**: headings, paragraphs, services, FAQs, values and so on.
- **Website → Contact details & footer**: phone, WhatsApp, email, hours, address, registration number.
- **Paragraphs**: leave an empty line between paragraphs.
- **Lists** (services, FAQs, steps): use **Add** to add one, drag to reorder, the bin icon to remove.
- **Founder photo**: About page → *Founder: photo* → choose a portrait photo (under 500 KB is best). Leave it empty to show "RB".
- Nothing goes live until you click **Publish**.

The legal pages (Privacy Notice, Terms) and the layout and colours are not in the editor on purpose. Ask your developer to change those.

## Contact form (already set up)

Netlify → **Site configuration → Environment variables** must have:
`SMTP_USER` = `info@finlume.co.za`, `SMTP_PASS` = that mailbox's password (marked secret), `MAIL_TO` = `info@finlume.co.za`, `FORM_SITE_NAME` = `Finlume`.

## Security

- The © trick only hides the door. The real lock is the GitHub sign-in: only accounts with write access to this repository can change anything. Turn on **two-factor login** on GitHub, Netlify, HostAfrica and the info@ mailbox.
- To let Rochelle edit with her own GitHub account: repository → **Settings → Collaborators → Add people**. (If the repository is private and Netlify then shows "Unrecognized Git contributor", either keep the repository public, which is safe because no passwords are stored in it, or edit with the GitHub account that is connected to Netlify.)
- The editor page is hidden from search engines and has its own strict security policy: it can only talk to this site, GitHub and Netlify's sign-in.
- Every public page keeps its strict fingerprint-based Content-Security-Policy, anti-clickjacking, HTTPS-only, rate limits and blocked hacking paths.

## Troubleshooting

| What you see | Fix |
|---|---|
| Editor says "Not Found" or "Failed to load config" after login | The OAuth provider isn't installed (step 2B), or the GitHub account has no write access to the repo |
| Login popup closes and nothing happens | Check the callback URL in the GitHub OAuth App is exactly `https://api.netlify.com/auth/done` |
| Published, but the live site didn't change | Netlify → Deploys: wait for the build to finish, or open the failed deploy log |
| Deploy log says `python3: command not found` | Netlify → Site configuration → Environment variables → add `PYTHON_VERSION` = `3.12`, then redeploy |

**Free plan limit:** every **Publish** in the editor starts one new Netlify deploy. Netlify's free plan gives 300 credits a month and each live deploy uses about 15, so roughly **20 publishes a month** (check Netlify → Billing → Usage). Make all your changes to a page, then publish once.
