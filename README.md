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
| `studio/` | The Website editor: login page and editor program (Decap CMS 3.17.1, stored here so no outside script is loaded) |
| `netlify/functions/contact.mjs` | Sends contact-form messages to info@finlume.co.za |
| `netlify/functions/cms-login.mjs`, `cms-github.mjs`, `netlify/lib/cms-auth.mjs` | The editor login and the safe relay to GitHub |
| `netlify.toml` | Netlify settings: build command, short addresses, security headers, rate limits |
| `fonts/`, images, `Finlume-Company-Profile.pdf` | Used to build the pages |

Do **not** upload any `.env` file. The mailbox password lives only in Netlify.

## 1. Upload to GitHub (replaces the old files)

1. Open the repository on GitHub. Delete the old website files (the old `.html` files and the old `netlify` folder).
2. **Add file → Upload files** → drag **everything** from this folder, including the folders `content`, `uploads`, `studio`, `fonts` and `netlify` → **Commit changes**.
3. Check the repo now shows `build.py`, `netlify.toml` and `content/home.json` at the top level.
4. Netlify builds the site by itself (the build settings are in `netlify.toml`). In Netlify → **Deploys**, the latest deploy should say **Published**.

## 2. Set up the editor login (once, about 10 minutes)

The editor has its own login page (username and password). Behind the scenes it saves your changes to GitHub with a private key that only Netlify knows.

**A. Create a GitHub key limited to this website**
1. On GitHub, signed in as the owner of this repository, go to **github.com/settings/personal-access-tokens/new** (Settings → Developer settings → Personal access tokens → **Fine-grained tokens** → **Generate new token**).
2. Token name: `Finlume website editor`. Expiration: the longest offered (put a reminder in your calendar to renew it).
3. **Repository access → Only select repositories** → choose this website's repository.
4. **Permissions → Repository permissions → Contents → Read and write**. (Metadata: Read-only is added automatically.) Leave everything else as "No access".
5. Click **Generate token** and copy it (it starts with `github_pat_` and is shown only once).

**B. Add the login settings to Netlify**
Netlify → **Site configuration → Environment variables → Add a variable** (or **Import from a .env file** and paste the contents of `finlume.env`):

| Key | Value | Secret? |
|---|---|---|
| `CMS_USERNAME` | `Admin` | No |
| `CMS_PASSWORD_HASH` | the long `scrypt:…` line from `finlume.env` (a scrambled form of the password, the password itself is never stored) | Yes |
| `GITHUB_TOKEN` | the `github_pat_…` key from step A | Yes |

Then **Deploys → Trigger deploy → Deploy site**.

**C. Try it**
1. On www.finlume.co.za click the **©** in the footer **5 times quickly** (or go to www.finlume.co.za/studio/).
2. Sign in with the username and password.
3. Open **Website → About page**, change something, click **Publish → Publish now**. Refresh the live site after a minute or two.

You stay signed in for 8 hours on that device. Use the menu at the top right of the editor to log out.

**Changing the password later:** ask your developer for a new `CMS_PASSWORD_HASH` value, replace it in Netlify and redeploy. Everyone is signed out automatically.

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

- The © trick only hides the door. The lock is the login: the password is checked on Netlify's server (never in the page), stored only as an scrypt hash, and limited to 5 attempts a minute per IP address with a delay after each wrong try. Use a long password and turn on **two-factor login** on GitHub, Netlify, HostAfrica and the info@ mailbox.
- The GitHub key never reaches the browser. The editor gets a signed 8-hour pass, and Netlify only passes on the GitHub requests the editor needs (reading and saving files in this one repository). Changes are saved as the GitHub account that created the key, so Netlify always recognises them.
- The editor page is hidden from search engines and has its own strict security policy: it can only talk to this website.
- Every public page keeps its strict fingerprint-based Content-Security-Policy, anti-clickjacking, HTTPS-only, rate limits and blocked hacking paths.

## Troubleshooting

| What you see | Fix |
|---|---|
| "The editor isn't set up yet" | Add the three `CMS_…`/`GITHUB_TOKEN` variables in Netlify, then redeploy |
| "Incorrect username or password" | Check spelling. The password is case-sensitive |
| "Too many attempts" | Wait one minute |
| Signed in, but the editor shows an error about the repo or "Bad credentials" | The GitHub key expired, or it doesn't include this repository with Contents: Read and write. Make a new key (step 2A), update `GITHUB_TOKEN`, redeploy |
| Published, but the live site didn't change | Netlify → Deploys: wait for the build to finish, or open the failed deploy log |
| Deploy log says `python3: command not found` | Netlify → Environment variables → add `PYTHON_VERSION` = `3.12`, then redeploy |

**Free plan limit:** every **Publish** in the editor starts one new Netlify deploy. Netlify's free plan gives 300 credits a month and each live deploy uses about 15, so roughly **20 publishes a month** (check Netlify → Billing → Usage). Make all your changes to a page, then publish once.
