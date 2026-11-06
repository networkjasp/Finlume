# Contact form built into each website (Netlify, free)

Each website sends its own form to its own inbox, for example
**www.finlume.co.za → info@finlume.co.za**. No outside form service is involved; the email is sent by the website's own mailbox at your hosting company (HostAfrica/cPanel).

## For each website (about 10 minutes)

1. **Copy the sender file.** Put `netlify/functions/contact.mjs` in the website's GitHub repository, keeping the folder path `netlify/functions/`. On GitHub, use **Add file → Upload files** and *drag* the `netlify` folder onto the page.
2. **Add the form.** Paste `contact-form-snippet.html` into the contact page and change `data-email` and `data-wa` (used only if sending ever fails).
3. **Add the mailbox login in Netlify.** Go to **Site configuration → Environment variables → Add a variable**:

   | Name | Example | Notes |
   |---|---|---|
   | `SMTP_USER` | `rochelle@finlume.co.za` | A real mailbox on the website's domain (cPanel → Email Accounts) |
   | `SMTP_PASS` | (mailbox password) | Tick **Contains secret values** |
   | `MAIL_TO` | `info@finlume.co.za` | Where enquiries should arrive |
   | `SITE_NAME` | `Finlume` | Shown in the email subject |

   If the mail server isn't `mail.<domain>`, also add `SMTP_HOST` (cPanel → Email Accounts → Connect Devices shows it).
4. **Redeploy.** Go to **Deploys → Trigger deploy → Deploy site**.
5. **Test.** Wait a few seconds after the page loads, then send a message. It should arrive at `MAIL_TO`, and **Reply** goes to the visitor.

## What's built in

- The form is accepted only from the website itself. Other sites can't use it.
- Every field is checked on the server; email headers can't be tampered with.
- Hidden bot trap, plus a block on instant "bot-speed" submissions.
- Netlify rate limit: max 5 messages per minute per visitor.
- The mailbox password stays in Netlify, never in the website files.
- If sending ever fails, the visitor gets **Send by email / Send on WhatsApp** buttons with the message already written.

## Cost

R0. It uses Netlify Functions on the free plan and your existing hosting mailbox. Contact forms use a tiny share of Netlify's free allowance.
