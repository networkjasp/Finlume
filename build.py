# -*- coding: utf-8 -*-
"""Builds the Finlume website.

Output 1: dist/   -> the Netlify site. Every page is ONE self-contained file
                     (styles, scripts, fonts and logo are inside the HTML), so
                     uploading the files is all that's needed, no folders.
Output 2: showcase.html -> the same site as a single preview page (hash navigation).
"""
import base64, hashlib, html, os, shutil, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import *

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts") + "/"  # Latin subsets (smaller downloads)
E = html.escape


def b64(path, mime):
    with open(path, "rb") as f:
        return "data:%s;base64,%s" % (mime, base64.b64encode(f.read()).decode())


MARK = b64(os.path.join(HERE, "mark.png"), "image/png")
MARK_W = b64(os.path.join(HERE, "mark_white.png"), "image/png")
COVER = b64(os.path.join(HERE, "cover.jpg"), "image/jpeg")
FAVICON = b64(os.path.join(HERE, "favicon.png"), "image/png")

FONT_FACES = ""
for fam, w, st, fn in [("Montserrat", 500, "normal", "montserrat-latin-500-normal"), ("Montserrat", 600, "normal", "montserrat-latin-600-normal"),
                       ("Montserrat", 500, "italic", "montserrat-latin-500-italic"),
                       ("Inter", 400, "normal", "inter-latin-400-normal"), ("Inter", 600, "normal", "inter-latin-600-normal")]:
    FONT_FACES += '@font-face{font-family:"%s";font-weight:%d;font-style:%s;font-display:swap;src:url(%s) format("woff2")}\n' % (
        fam, w, st, b64(FONTS + fn + ".woff2", "font/woff2"))

# ---------------------------------------------------------------- icons
def svg(d, fill=False):
    if fill:
        return '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false">%s</svg>' % d
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true" focusable="false">%s</svg>' % d)

ICONS = {
    "ledger": svg('<path d="M4 19.5V5a2 2 0 0 1 2-2h13v16H6.5A2.5 2.5 0 0 0 4 21.5"/><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H19"/><path d="M9 7h6M9 11h4"/>'),
    "payroll": svg('<rect x="2.5" y="6" width="19" height="12" rx="2"/><circle cx="12" cy="12" r="2.6"/><path d="M6 9.5v5M18 9.5v5"/>'),
    "tax": svg('<path d="M5 3h14v18l-3-2-2 2-2-2-2 2-2-2-3 2z"/><path d="M9 14l6-6"/><circle cx="9.5" cy="8.5" r="1"/><circle cx="14.5" cy="13.5" r="1"/>'),
    "statements": svg('<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/><path d="M9 13h6M9 17h6M9 9h2"/>'),
    "chart": svg('<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 6-7"/><path d="M16 7h4v4"/>'),
    "compass": svg('<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>'),
    "building": svg('<path d="M4 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16"/><path d="M16 9h2a2 2 0 0 1 2 2v10"/><path d="M2 21h20"/><path d="M8 7h4M8 11h4M8 15h4"/>'),
    "team": svg('<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7"/><path d="M18 14a6.5 6.5 0 0 1 3.5 6"/>'),
    "shield": svg('<path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>'),
    "calendar": svg('<rect x="3" y="4.5" width="18" height="16.5" rx="2"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4"/><path d="M9 15l2 2 4-4"/>'),
    "chat": svg('<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20.5l1.4-4.9A8 8 0 1 1 21 12z"/><path d="M8.5 10.5h7M8.5 13.5h4.5"/>'),
    "growth": svg('<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>'),
    "user": svg('<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>'),
    "rocket": svg('<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>'),
    "heart": svg('<path d="M12 20.5s-8-4.7-8-11A4.5 4.5 0 0 1 12 6.6 4.5 4.5 0 0 1 20 9.5c0 6.3-8 11-8 11z"/>'),
    "briefcase": svg('<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/><path d="M3 12.5h18"/>'),
    "pin": svg('<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>'),
    "eye": svg('<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>'),
    "target": svg('<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>'),
    "handshake": svg('<path d="M3 12l4-4 4 2 3-2 3 1 4 3"/><path d="M7 14l3 3 2-1 2 2 3-3"/>'),
    "lock": svg('<rect x="4" y="10.5" width="16" height="10.5" rx="2"/><path d="M8 10.5V7a4 4 0 0 1 8 0v3.5"/><circle cx="12" cy="15.5" r="1.3"/>'),
    "clock": svg('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>'),
    "phone": svg('<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>'),
    "mail": svg('<rect x="2.5" y="4.5" width="19" height="15" rx="2"/><path d="M3 6.5l9 6.5 9-6.5"/>'),
    "arrow": svg('<path d="M5 12h14M13 6l6 6-6 6"/>'),
    "download": svg('<path d="M12 3v12"/><path d="M7 10l5 5 5-5"/><path d="M5 21h14"/>'),
    "check": svg('<path d="M5 12.5l4.5 4.5L19 7.5"/>'),
    "plus": svg('<path d="M12 5v14M5 12h14"/>'),
    "whatsapp": svg('<path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.16-.17.2-.35.22-.64.08-.3-.15-1.26-.47-2.39-1.48-.88-.79-1.48-1.76-1.65-2.06-.17-.3-.02-.46.13-.6.13-.14.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.03-.52-.07-.15-.67-1.61-.92-2.2-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48 0 1.46 1.07 2.88 1.21 3.07.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.7.63.71.22 1.36.19 1.87.12.57-.09 1.76-.72 2-1.41.25-.7.25-1.29.18-1.41-.08-.13-.27-.2-.57-.35m-5.42 7.4h-.01a9.87 9.87 0 0 1-5.03-1.38l-.36-.21-3.74.98 1-3.65-.24-.37a9.86 9.86 0 0 1-1.51-5.26c0-5.45 4.44-9.88 9.89-9.88 2.64 0 5.12 1.03 6.99 2.9a9.83 9.83 0 0 1 2.89 6.99c0 5.45-4.44 9.88-9.88 9.88m8.41-18.3A11.82 11.82 0 0 0 12.05 0C5.5 0 .16 5.34.16 11.89c0 2.1.55 4.14 1.59 5.95L.06 24l6.3-1.65a11.88 11.88 0 0 0 5.68 1.45h.01c6.55 0 11.89-5.34 11.89-11.89 0-3.18-1.24-6.17-3.48-8.41z"/>', True),
}
I = ICONS

WA = "https://wa.me/%s?text=%s" % (WA_NUMBER, urllib.parse.quote(WA_TEXT))

# ---------------------------------------------------------------- CSS
CSS = FONT_FACES + r"""
/* Layout concept: calm white ledger pages framed by navy "covers"; the feather sweep from the logo is the one decorative motif. */
:root{
  --navy:#0B1F4B;--navy-2:#102A62;--royal:#1E4FB8;--aqua:#3BB8D6;--gold:#C9A55A;--gold-d:#7A5B1E;--gold-l:#E7D2A0;
  --ink:#16202E;--slate:#545F70;--paper:#F7F5F1;--mist:#EEF2F8;--line:#DEE4ED;--white:#FFFFFF;--wa:#25D366;
  --f-display:"Montserrat","Segoe UI",Arial,sans-serif;--f-body:"Inter","Segoe UI",system-ui,Arial,sans-serif;
  --r:16px;--wrap:1180px;--gut:max(20px,env(safe-area-inset-left,0px));--gut-r:max(20px,env(safe-area-inset-right,0px));
  --sec:clamp(64px,8vw,112px);--shadow:0 1px 2px rgba(11,31,75,.05),0 16px 40px -16px rgba(11,31,75,.22);
  color-scheme:light;
}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;scroll-padding-top:90px}
body{margin:0;background:var(--white);color:var(--ink);font:400 17px/1.65 var(--f-body);-webkit-font-smoothing:antialiased;overflow-x:hidden}
img,svg{display:block;max-width:100%}
a{color:var(--royal);text-underline-offset:3px}
h1,h2,h3{font-family:var(--f-display);font-weight:600;color:var(--navy);line-height:1.15;margin:0 0 .55em;text-wrap:balance;letter-spacing:-.01em}
h1{font-size:clamp(2.3rem,5.4vw,4.1rem);letter-spacing:-.025em}
h2{font-size:clamp(1.75rem,3.3vw,2.55rem)}
h3{font-size:1.14rem;letter-spacing:0}
p{margin:0 0 1em}p:last-child{margin-bottom:0}
ul,ol{margin:0;padding:0;list-style:none}
:focus-visible{outline:3px solid var(--aqua);outline-offset:3px;border-radius:6px}
.skip{position:absolute;left:-999px;top:8px;z-index:100;background:var(--navy);color:#fff;padding:10px 16px;border-radius:8px}
.skip:focus{left:12px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.wrap{max-width:calc(var(--wrap) + 40px);margin:0 auto;padding-left:var(--gut);padding-right:var(--gut-r)}
.sec{padding-block:var(--sec)}
.bg-paper{background:var(--paper)}.bg-mist{background:var(--mist)}
.eyebrow{display:inline-flex;align-items:center;gap:12px;font:600 .74rem/1.2 var(--f-display);letter-spacing:.22em;text-transform:uppercase;color:var(--gold-d);margin:0 0 18px}
.eyebrow::before{content:"";width:28px;height:1.5px;background:var(--gold)}
.dark .eyebrow,.hero .eyebrow,.phero .eyebrow,.cta-box .eyebrow{color:var(--gold-l)}
.lead{font-size:1.14rem;color:var(--slate);max-width:62ch}
.head{max-width:700px;margin-bottom:clamp(36px,5vw,56px)}
.head.c{margin-inline:auto;text-align:center}.head.c .eyebrow::after{content:"";width:28px;height:1.5px;background:var(--gold)}
.head.c .lead{margin-inline:auto}
/* buttons */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;min-height:50px;padding:0 26px;border-radius:999px;border:1.5px solid transparent;font:600 .8rem/1 var(--f-display);letter-spacing:.1em;text-transform:uppercase;text-decoration:none;cursor:pointer;transition:transform .2s,box-shadow .2s,background .2s,color .2s}
.btn svg{width:18px;height:18px}
.btn:hover{transform:translateY(-2px)}
.btn-gold{background:var(--gold);color:var(--navy)}.btn-gold:hover{background:var(--gold-l);color:var(--navy);box-shadow:0 12px 26px -12px rgba(201,165,90,.9)}
.btn-navy{background:var(--royal);color:#fff}.btn-navy:hover{background:var(--navy);color:#fff;box-shadow:0 12px 26px -12px rgba(30,79,184,.8)}
.btn-line{border-color:var(--line);color:var(--navy);background:#fff}.btn-line:hover{border-color:var(--royal);color:var(--royal)}
.btn-ghost{border-color:rgba(255,255,255,.35);color:#fff}.btn-ghost:hover{background:rgba(255,255,255,.1);color:#fff}
.btn-row{display:flex;flex-wrap:wrap;gap:14px}
/* header */
.hdr{position:sticky;top:env(safe-area-inset-top,0px);z-index:50;background:#fff;border-bottom:1px solid transparent;transition:border-color .2s,box-shadow .2s}
.hdr.scrolled{border-color:var(--line);box-shadow:0 8px 24px -18px rgba(11,31,75,.5)}
.hdr-in{display:flex;align-items:center;justify-content:space-between;gap:20px;min-height:78px}
.brand{display:flex;align-items:center;gap:12px;text-decoration:none}
.brand-mark{width:38px;height:42px;background:url(%%MARK%%) center/contain no-repeat;flex:none}
.brand-txt{display:flex;flex-direction:column;line-height:1}
.brand-name{font:600 1.32rem/1 var(--f-display);letter-spacing:.24em;color:var(--ink)}
.brand-sub{font:500 .52rem/1 var(--f-display);letter-spacing:.2em;color:var(--slate);margin-top:6px}
.brand.light .brand-name{color:#fff}.brand.light .brand-sub{color:#AEBBD6}.brand.light .brand-mark{background-image:url(%%MARK%%)}
.nav{display:flex;align-items:center;gap:30px}
.nav-list{display:flex;gap:28px}
.nav-list a{font:600 .78rem/1 var(--f-display);letter-spacing:.12em;text-transform:uppercase;color:var(--navy);text-decoration:none;padding:10px 0;position:relative}
.nav-list a::after{content:"";position:absolute;left:0;right:0;bottom:2px;height:2px;background:var(--gold);transform:scaleX(0);transition:transform .25s}
.nav-list a:hover::after,.nav-list a[aria-current="page"]::after{transform:scaleX(1)}
.menu-btn{display:none;width:46px;height:46px;border-radius:12px;border:1.5px solid var(--line);background:#fff;cursor:pointer;align-items:center;justify-content:center}
.menu-btn span,.menu-btn span::before,.menu-btn span::after{display:block;width:20px;height:2px;background:var(--navy);border-radius:2px;position:relative;transition:transform .25s,background .25s}
.menu-btn span::before,.menu-btn span::after{content:"";position:absolute;left:0}
.menu-btn span::before{top:-6px}.menu-btn span::after{top:6px}
.menu-btn[aria-expanded="true"] span{background:transparent}
.menu-btn[aria-expanded="true"] span::before{transform:translateY(6px) rotate(45deg)}
.menu-btn[aria-expanded="true"] span::after{transform:translateY(-6px) rotate(-45deg)}
/* hero */
.hero{position:relative;overflow:hidden;background:linear-gradient(140deg,#081839 0%,var(--navy) 38%,#163C8F 78%,#1E5BB0 100%);color:#D7E1F3}
.hero h1,.hero h2,.hero h3{color:#fff}
.sweep{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}
.sweep path{fill:none;stroke-linecap:round}
.sweep .s1{stroke:rgba(59,184,214,.35);stroke-width:2}
.sweep .s2{stroke:rgba(201,165,90,.75);stroke-width:1.6}
.sweep .s3{stroke:rgba(255,255,255,.1);stroke-width:1.4}
.sweep .s4{stroke:rgba(59,184,214,.18);stroke-width:26}
.js .sweep .draw{stroke-dasharray:2400;stroke-dashoffset:2400;animation:draw 2.6s cubic-bezier(.3,.6,.2,1) .2s forwards}
@keyframes draw{to{stroke-dashoffset:0}}
.hero-in{position:relative;display:grid;grid-template-columns:1.15fr .85fr;gap:clamp(36px,6vw,80px);align-items:center;padding-block:clamp(72px,9vw,120px)}
.hero .lead{color:#C9D5EC}
.grad-word{background:linear-gradient(90deg,#7FD6EA,var(--gold-l));-webkit-background-clip:text;background-clip:text;color:transparent}
.hero .btn-row{margin-top:34px}
/* month-end card */
.mcard{background:rgba(255,255,255,.97);color:var(--ink);border-radius:22px;padding:26px 26px 22px;box-shadow:0 40px 80px -30px rgba(0,0,0,.55);position:relative}
.mcard-top{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:16px}
.mcard-title{font:600 1.02rem/1.2 var(--f-display);color:var(--navy);margin:0}
.mcard-month{font:600 .7rem/1 var(--f-display);letter-spacing:.16em;text-transform:uppercase;color:var(--slate);background:var(--mist);padding:7px 10px;border-radius:999px;white-space:nowrap}
.mlist li{display:flex;align-items:center;gap:12px;padding:12px 0;border-top:1px solid var(--line);font-size:.95rem}
.mlist .tick{width:26px;height:26px;border-radius:50%;flex:none;display:grid;place-items:center;background:linear-gradient(135deg,var(--royal),var(--aqua));color:#fff}
.mlist .tick svg{width:15px;height:15px}
.mlist .lbl{flex:1;min-width:0}
.pill{font:600 .66rem/1 var(--f-display);letter-spacing:.1em;text-transform:uppercase;padding:6px 9px;border-radius:999px;white-space:nowrap}
.pill.ok{background:#E3F5EC;color:#14724A}.pill.wait{background:#FBF1DC;color:#8A6416}
.mcard-note{font-size:.76rem;color:var(--slate);margin-top:12px}
/* trust */
.trust{border-bottom:1px solid var(--line);background:#fff}
.trust ul{display:flex;flex-wrap:wrap;justify-content:space-between;gap:14px 28px;padding-block:22px}
.trust li{display:flex;align-items:center;gap:10px;font:600 .8rem/1.2 var(--f-display);letter-spacing:.04em;color:var(--navy)}
.trust li svg{width:20px;height:20px;color:var(--royal)}
/* split intro */
.split{display:grid;grid-template-columns:1fr 1.15fr;gap:clamp(28px,6vw,90px);align-items:start}
.split .txt{color:var(--slate);font-size:1.06rem}
/* cards */
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
.card{background:#fff;border:1px solid var(--line);border-radius:var(--r);padding:28px 26px;display:flex;flex-direction:column;transition:transform .25s,box-shadow .25s,border-color .25s}
.card:hover{transform:translateY(-4px);box-shadow:var(--shadow);border-color:transparent}
.card p{color:var(--slate);font-size:.95rem}
.ico{width:50px;height:50px;border-radius:14px;display:grid;place-items:center;flex:none;background:linear-gradient(135deg,var(--navy),var(--royal) 70%,var(--aqua));color:#fff;margin-bottom:20px;box-shadow:0 10px 20px -10px rgba(30,79,184,.7)}
.ico svg{width:24px;height:24px}
.more{margin-top:auto;padding-top:18px;display:inline-flex;align-items:center;gap:8px;font:600 .72rem/1 var(--f-display);letter-spacing:.14em;text-transform:uppercase;color:var(--royal);text-decoration:none}
.more svg{width:16px;height:16px;transition:transform .2s}.card:hover .more svg{transform:translateX(4px)}
.card.feature{background:linear-gradient(150deg,var(--navy),#17408F);border:0;color:#D3DDF0;position:relative;overflow:hidden}
.card.feature h3{color:#fff}.card.feature p{color:#C5D2EA}
.card.feature .btn{margin-top:auto;align-self:flex-start}
/* deadlines */
.dl{display:grid;grid-template-columns:repeat(5,1fr);gap:0;background:#fff;border:1px solid var(--line);border-radius:20px;overflow:hidden}
.dl li{padding:26px 22px;border-left:1px solid var(--line);display:flex;flex-direction:column;gap:8px}
.dl li:first-child{border-left:0}
.dl-when{font:600 1.18rem/1.15 var(--f-display);color:var(--navy);font-variant-numeric:tabular-nums}
.dl-freq{font-size:.78rem;color:var(--slate)}
.dl-form{align-self:flex-start;font:600 .7rem/1 var(--f-display);letter-spacing:.12em;color:var(--royal);background:var(--mist);padding:7px 10px;border-radius:8px;margin-top:6px}
.dl-what{font-size:.9rem;color:var(--slate);margin:0}
.fine{font-size:.82rem;color:var(--slate);margin-top:16px}
/* why */
.why{display:grid;grid-template-columns:repeat(2,1fr);gap:30px 40px}
.why-item{display:flex;gap:18px}
.why-item .ico{width:46px;height:46px;margin:0}
.why-item h3{margin-bottom:6px}.why-item p{color:var(--slate);font-size:.96rem}
.why-wrap{display:grid;grid-template-columns:1.25fr 1fr;gap:clamp(36px,5vw,70px);align-items:start}
/* compare */
.cmp{background:#fff;border-radius:20px;box-shadow:var(--shadow);overflow:hidden}
.cmp-row{display:grid;grid-template-columns:1.5fr 1fr 1fr;border-top:1px solid var(--line)}
.cmp-row>*{padding:14px 18px;font-size:.93rem}
.cmp-row>:first-child{font-weight:600;color:var(--ink)}
.cmp-head{border-top:0}
.cmp-head>*{font:600 .7rem/1.3 var(--f-display);letter-spacing:.14em;text-transform:uppercase;color:var(--slate);background:var(--paper)}
.cmp-head>:last-child{background:var(--navy);color:#fff}
.cmp .no{color:var(--slate)}
.cmp .yes{font-weight:600;color:var(--royal);background:#F0F8FC}
.cmp-cap{font:600 1rem/1.3 var(--f-display);color:var(--navy);padding:20px 18px 6px;margin:0}
/* steps */
.steps{display:grid;grid-template-columns:repeat(5,1fr);gap:24px;counter-reset:s;position:relative}
.steps::before{content:"";position:absolute;left:24px;right:24px;top:24px;height:1.5px;background:linear-gradient(90deg,var(--gold),rgba(201,165,90,.25))}
.step{position:relative}
.step-n{width:48px;height:48px;border-radius:50%;background:#fff;border:1.5px solid var(--gold);display:grid;place-items:center;font:600 .9rem/1 var(--f-display);color:var(--navy);margin-bottom:18px;position:relative}
.step h3{text-transform:uppercase;letter-spacing:.14em;font-size:.88rem}
.step p{color:var(--slate);font-size:.93rem}
/* serve (dark band) */
.dark{background:linear-gradient(150deg,#081839,var(--navy) 50%,#143A86);color:#C9D5EC;position:relative;overflow:hidden}
.dark h2,.dark h3{color:#fff}.dark .lead{color:#C2CFE8}
.serve{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;position:relative}
.serve li{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);border-radius:var(--r);padding:24px;display:flex;gap:16px;align-items:flex-start}
.serve li svg{width:24px;height:24px;color:var(--aqua);flex:none;margin-top:2px}
.serve h3{margin-bottom:4px;font-size:1.04rem}.serve p{font-size:.92rem;color:#B9C7E2}
.serve li.gold{background:var(--gold);border-color:var(--gold)}
.serve li.gold h3,.serve li.gold p,.serve li.gold svg{color:var(--navy)}
/* faq */
.faq-wrap{display:grid;grid-template-columns:.85fr 1.3fr;gap:clamp(28px,5vw,72px);align-items:start}
.faq details{border-bottom:1px solid var(--line)}
.faq details:first-child{border-top:1px solid var(--line)}
.faq summary{list-style:none;cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:18px;padding:20px 0;font:600 1.02rem/1.4 var(--f-display);color:var(--navy)}
.faq summary::-webkit-details-marker{display:none}
.faq summary svg{width:22px;height:22px;flex:none;color:var(--royal);transition:transform .25s}
.faq details[open] summary svg{transform:rotate(45deg)}
.faq details p{color:var(--slate);padding:0 40px 22px 0;margin:0}
/* profile band */
.prof{display:grid;grid-template-columns:.8fr 1.2fr;gap:clamp(36px,6vw,90px);align-items:center}
.prof-img{justify-self:center;width:min(300px,80%);position:relative}
.prof-img img{width:100%;height:auto;border-radius:6px;box-shadow:0 34px 60px -24px rgba(11,31,75,.6);transform:rotate(-4deg);transition:transform .4s}
.prof-img::before{content:"";position:absolute;inset:6% -8% -4% 12%;background:var(--mist);border-radius:8px;transform:rotate(5deg)}
.prof-img:hover img{transform:rotate(-2deg) translateY(-4px)}
.checks{display:grid;gap:10px;margin:22px 0 30px}
.checks li{display:flex;gap:12px;align-items:flex-start;font-size:.97rem}
.checks li svg{width:20px;height:20px;flex:none;color:#fff;background:linear-gradient(135deg,var(--royal),var(--aqua));border-radius:50%;padding:3px;margin-top:2px}
.prof .checks{grid-template-columns:1fr 1fr}
/* CTA */
.cta{padding-block:clamp(56px,7vw,90px)}
.cta-box{position:relative;overflow:hidden;border-radius:26px;background:linear-gradient(120deg,var(--navy),var(--royal) 70%,#2C8FC2);color:#D3DFF3;padding:clamp(34px,5vw,60px);display:flex;align-items:center;justify-content:space-between;gap:28px;flex-wrap:wrap}
.cta-box h2{color:#fff;margin-bottom:8px}
.cta-box p{max-width:52ch}
.cta-box>*{position:relative}
.cta-mark{position:absolute!important;right:-30px;bottom:-60px;width:260px;height:290px;background:url(%%MARK_W%%) center/contain no-repeat;opacity:.08}
/* inner page hero */
.phero{position:relative;overflow:hidden;background:linear-gradient(140deg,#081839,var(--navy) 45%,#174091);color:#C9D5EC}
.phero h1{color:#fff;font-size:clamp(2.1rem,4.6vw,3.4rem);max-width:18ch}
.phero .wrap{position:relative;padding-block:clamp(64px,8vw,104px)}
.phero .lead{color:#C4D1EA}
.chips{display:flex;flex-wrap:wrap;gap:10px;margin-top:28px}
.chips a{font:600 .74rem/1 var(--f-display);letter-spacing:.06em;color:#fff;text-decoration:none;padding:10px 14px;border-radius:999px;border:1px solid rgba(255,255,255,.25)}
.chips a:hover{background:rgba(255,255,255,.12)}
/* about */
.glance{margin-top:clamp(40px,5vw,64px);display:grid;grid-template-columns:repeat(5,1fr);background:#fff;border:1px solid var(--line);border-radius:18px;overflow:hidden}
.glance div{padding:22px 20px;border-left:1px solid var(--line)}
.glance div:first-child{border-left:0}
.g-k{display:block;font:600 .68rem/1 var(--f-display);letter-spacing:.18em;text-transform:uppercase;color:var(--gold-d);margin-bottom:8px}
.g-v{font:600 1rem/1.35 var(--f-display);color:var(--navy)}
.name{max-width:760px;margin:clamp(44px,6vw,70px) auto 0;text-align:center;font:500 clamp(1.25rem,2.4vw,1.7rem)/1.5 var(--f-display);color:var(--navy)}
.name b{color:var(--royal)}.name i{color:var(--gold-d)}.name small{color:var(--slate);font-size:.7em}
.founder{display:grid;grid-template-columns:.8fr 1.2fr;gap:clamp(32px,6vw,90px);align-items:center}
.f-photo{position:relative;max-width:420px;width:100%;aspect-ratio:5/6;border-radius:24px;background:linear-gradient(160deg,var(--navy),var(--royal) 70%,var(--aqua));display:grid;place-items:center;overflow:hidden;box-shadow:var(--shadow)}
.f-photo::before{content:"";position:absolute;inset:auto -20% -30% -10%;height:70%;background:url(%%MARK_W%%) center/contain no-repeat;opacity:.08}
.f-photo img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.f-photo.has-img::before{display:none}
.cms-key{cursor:default;-webkit-user-select:none;user-select:none}
.f-init{font:600 clamp(3.4rem,8vw,5.4rem)/1 var(--f-display);color:#fff;letter-spacing:.06em;position:relative}
.f-role{font:600 .76rem/1 var(--f-display);letter-spacing:.2em;text-transform:uppercase;color:var(--gold-d);margin:-6px 0 24px}
.quote{margin:26px 0 0;padding:20px 24px;background:var(--paper);border-left:3px solid var(--gold);border-radius:0 14px 14px 0}
.quote p{font:italic 500 1.08rem/1.55 var(--f-display);color:var(--navy)}
.quote cite{display:block;margin-top:10px;font:600 .7rem/1 var(--f-display);letter-spacing:.2em;text-transform:uppercase;color:var(--gold-d);font-style:normal}
.vm{display:grid;grid-template-columns:1fr 1fr;gap:22px}
.vm>div{border-radius:20px;padding:clamp(28px,4vw,44px);border:1px solid var(--line);background:#fff}
.vm>div.d{background:linear-gradient(150deg,var(--navy),#17408F);border:0;color:#D3DFF3}
.vm h2{font-size:1.4rem}.vm .d h2{color:#fff}
.vm p{font-size:1.1rem;line-height:1.7}
.values{display:grid;grid-template-columns:repeat(5,1fr);gap:16px}
.values .card{align-items:flex-start;padding:24px 22px}
/* services detail */
.svc{display:grid;grid-template-columns:1.2fr 1fr;gap:clamp(28px,5vw,64px);padding-block:clamp(40px,5vw,60px);border-top:1px solid var(--line);align-items:start}
.svc:first-child{border-top:0;padding-top:0}
.svc-n{font:600 .74rem/1 var(--f-display);letter-spacing:.2em;color:var(--gold-d);margin-bottom:14px;display:block}
.svc h2{font-size:clamp(1.5rem,2.6vw,2rem)}
.svc .sum{font-weight:600;color:var(--ink)}
.svc p{color:var(--slate)}
.svc .incl{background:var(--paper);border-radius:18px;padding:26px 26px 24px}
.incl h3{font:600 .72rem/1 var(--f-display);letter-spacing:.2em;text-transform:uppercase;color:var(--gold-d);margin-bottom:14px}
.incl .checks{margin:0}
.engage{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
.engage .card{padding:30px 28px}
.engage .best{margin-top:auto;padding-top:16px;border-top:1px solid var(--line);font-size:.86rem;color:var(--slate)}
.engage .card.feature .best{border-color:rgba(255,255,255,.18);color:var(--gold-l)}
.engage .card.feature .checks li{color:#E3EAF7}
.engage .checks{margin:18px 0 22px}
/* contact */
.contact{display:grid;grid-template-columns:.85fr 1.25fr;gap:clamp(28px,4vw,48px);align-items:start}
.cards{display:grid;gap:12px}
.cc{display:flex;gap:14px;align-items:center;background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px 18px;text-decoration:none;color:var(--ink)}
a.cc:hover{border-color:var(--royal)}
.cc svg{width:22px;height:22px;color:var(--royal);flex:none}
.cc .k{display:block;font:600 .66rem/1 var(--f-display);letter-spacing:.18em;text-transform:uppercase;color:var(--slate);margin-bottom:5px}
.cc .v{font-weight:600;font-size:.98rem;overflow-wrap:anywhere}
.wa-card{background:linear-gradient(150deg,var(--navy),#17408F);color:#D3DFF3;border-radius:16px;padding:24px;margin-top:6px}
.wa-h{font:600 1.14rem/1.2 var(--f-display);color:#fff;margin:0 0 6px}
.btn-wa{background:var(--wa);color:#073B1E;margin-top:16px}.btn-wa:hover{background:#4BE07F;color:#073B1E}
.form{background:#fff;border:1px solid var(--line);border-radius:22px;padding:clamp(24px,4vw,40px);box-shadow:var(--shadow)}
.fgrid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.field{display:flex;flex-direction:column;gap:7px;min-width:0}
.field.full{grid-column:1/-1}
.field label{font:600 .72rem/1.2 var(--f-display);letter-spacing:.12em;text-transform:uppercase;color:var(--navy)}
.field input,.field select,.field textarea{font:400 1rem/1.4 var(--f-body);color:var(--ink);background:var(--paper);border:1.5px solid var(--line);border-radius:12px;padding:13px 14px;width:100%}
.field textarea{min-height:140px;resize:vertical}
.field input:focus,.field select:focus,.field textarea:focus{outline:none;border-color:var(--royal);background:#fff;box-shadow:0 0 0 4px rgba(30,79,184,.12)}
.field [aria-invalid="true"]{border-color:#C0392B}
.err{font-size:.8rem;color:#B42318;min-height:1em}
.hint{font-size:.82rem;color:var(--slate)}
.btn[disabled]{opacity:.75;cursor:wait;transform:none}
.field label.consent{display:flex;gap:12px;align-items:flex-start;font:400 .92rem/1.5 var(--f-body);letter-spacing:0;text-transform:none;color:var(--slate)}
.consent input{width:20px;height:20px;margin-top:2px;flex:none;accent-color:var(--royal)}
.hp{position:absolute;left:-5000px;width:1px;height:1px;overflow:hidden}
.form-msg{border-radius:12px;padding:14px 16px;font-size:.95rem;margin-top:16px}.form-msg p{margin:0 0 12px}.form-msg .btn-row{gap:10px}
.form-msg.ok{background:#E3F5EC;color:#0E5C3A}.form-msg.bad{background:#FDECEA;color:#8A1C12}
/* prose */
.prose{max-width:760px;margin:0 auto}
.prose h2{font-size:1.25rem;margin-top:2em}
.prose p,.prose li{color:var(--slate)}
.prose ul{list-style:disc;padding-left:1.3em;margin:0 0 1em}
.prose li{margin:.3em 0}
/* center pages */
.center{text-align:center;padding-block:clamp(80px,12vw,150px)}
.center .lead{margin-inline:auto}
.center .btn-row{justify-content:center;margin-top:28px}
.big-n{font:600 clamp(5rem,14vw,9rem)/1 var(--f-display);background:linear-gradient(90deg,var(--royal),var(--aqua));-webkit-background-clip:text;background-clip:text;color:transparent;margin-bottom:10px}
.tick-big{width:76px;height:76px;border-radius:50%;margin:0 auto 24px;display:grid;place-items:center;background:var(--gold);color:var(--navy)}
.tick-big svg{width:36px;height:36px}
/* footer */
.ftr{background:#071531;color:#9FAECB;position:relative;overflow:hidden;font-size:.94rem}
.ftr::before{content:"";position:absolute;left:0;right:0;top:0;height:3px;background:linear-gradient(90deg,var(--gold),var(--aqua),var(--royal))}
.ftr-top{display:grid;grid-template-columns:1.4fr 1fr 1.2fr 1.3fr;gap:36px;padding-block:64px 40px}
.ftr h2{font:600 .72rem/1 var(--f-display);letter-spacing:.2em;text-transform:uppercase;color:var(--gold-l);margin-bottom:18px}
.ftr a{color:#D4DDEE;text-decoration:none}.ftr a:hover{color:#fff;text-decoration:underline}
.ftr li{margin-bottom:10px}
.ftr .brand{margin-bottom:18px}
.ftr-c li{display:flex;gap:10px;align-items:flex-start}
.ftr-c svg{width:18px;height:18px;color:var(--aqua);flex:none;margin-top:3px}
.ftr-bot{border-top:1px solid rgba(255,255,255,.1);padding-block:22px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;font-size:.84rem}
.nw{white-space:nowrap}
.ftr-bot .tag{font:italic 500 .76rem/1 var(--f-display);letter-spacing:.18em;text-transform:uppercase;color:var(--gold-l)}
/* whatsapp float */
.wa{position:fixed;right:calc(20px + env(safe-area-inset-right,0px));bottom:calc(20px + env(safe-area-inset-bottom,0px));z-index:60;width:60px;height:60px;border-radius:50%;background:var(--wa);color:#fff;display:grid;place-items:center;box-shadow:0 12px 28px -8px rgba(18,140,70,.7);transition:transform .2s}
.wa:hover{transform:scale(1.07)}
.wa svg{width:32px;height:32px}
.wa::before{content:"";position:absolute;inset:0;border-radius:50%;border:2px solid var(--wa);animation:ping 2.6s ease-out 1.5s 4}
@keyframes ping{0%{transform:scale(1);opacity:.7}80%,100%{transform:scale(1.55);opacity:0}}
/* cookie notice */
.cookie{position:fixed;left:calc(16px + env(safe-area-inset-left,0px));bottom:calc(16px + env(safe-area-inset-bottom,0px));z-index:70;max-width:440px;background:#fff;color:var(--ink);border:1px solid var(--line);border-radius:16px;padding:18px 20px;box-shadow:0 24px 50px -18px rgba(11,31,75,.45);font-size:.9rem}
.cookie p{margin:0 0 12px;color:var(--slate)}.cookie strong{color:var(--navy)}
.cookie-btns{display:flex;gap:10px;flex-wrap:wrap}
.cookie .btn{min-height:42px;padding:0 18px;font-size:.72rem;width:auto}
/* showcase */
.show-bar{background:var(--gold);color:var(--navy);text-align:center;font:600 .78rem/1.4 var(--f-display);letter-spacing:.06em;padding:8px var(--gut)}
.view[hidden]{display:none!important}
/* motion: content is always visible; only a gentle entrance on the hero */
.js .rise{animation:rise .8s cubic-bezier(.2,.65,.3,1) both}
.js .rise.d2{animation-delay:.12s}.js .rise.d3{animation-delay:.24s}
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}html{scroll-behavior:auto}.js .sweep .draw{stroke-dashoffset:0}}
/* responsive */
@media (max-width:1080px){
  .grid4{grid-template-columns:repeat(2,1fr)}
  .dl{grid-template-columns:repeat(3,1fr)}.dl li:nth-child(4){border-left:0}.dl li:nth-child(n+4){border-top:1px solid var(--line)}
  .why-wrap,.faq-wrap{grid-template-columns:1fr}
  .steps{grid-template-columns:repeat(3,1fr)}.steps::before{display:none}
  .values{grid-template-columns:repeat(3,1fr)}
  .glance{grid-template-columns:repeat(3,1fr)}.glance div:nth-child(4){border-left:0}.glance div:nth-child(n+4){border-top:1px solid var(--line)}
  .ftr-top{grid-template-columns:1fr 1fr}
}
@media (max-width:920px){
  .menu-btn{display:inline-flex}
  .nav{position:absolute;left:0;right:0;top:100%;flex-direction:column;align-items:stretch;gap:18px;background:#fff;padding:18px var(--gut) 26px;border-bottom:1px solid var(--line);box-shadow:0 24px 40px -24px rgba(11,31,75,.45);display:none}
  .nav.open{display:flex}
  .nav-list{flex-direction:column;gap:0}
  .nav-list a{display:block;padding:15px 0;border-bottom:1px solid var(--mist)}
  .nav-list a::after{display:none}
  .hero-in,.split,.prof,.founder,.contact,.svc{grid-template-columns:1fr}
  .grid3,.serve,.engage,.vm{grid-template-columns:1fr 1fr}
  .engage{grid-template-columns:1fr}
}
@media (max-width:640px){
  body{font-size:16px}
  .grid4,.grid3,.serve,.vm,.why,.values,.fgrid,.prof .checks{grid-template-columns:1fr}
  .dl{grid-template-columns:1fr}.dl li{border-left:0!important;border-top:1px solid var(--line)}.dl li:first-child{border-top:0}
  .steps{grid-template-columns:1fr}
  .glance{grid-template-columns:1fr 1fr}.glance div{border-left:0!important;border-top:1px solid var(--line)}.glance div:nth-child(-n+2){border-top:0}.glance div:nth-child(even){border-left:1px solid var(--line)!important}.glance div:nth-child(5){grid-column:1/-1}
  .cmp-row{grid-template-columns:1.3fr 1fr 1fr}.cmp-row>*{padding:12px 10px;font-size:.84rem}
  .trust ul{justify-content:flex-start}
  .ftr-top{grid-template-columns:1fr}
  .btn{width:100%}.btn-row{flex-direction:column}
  .hdr .nav .btn{width:100%}
  .brand-name{font-size:1.15rem}
  .cookie{right:calc(16px + env(safe-area-inset-right,0px));max-width:none;bottom:calc(90px + env(safe-area-inset-bottom,0px))}
  .pill{font-size:.56rem;padding:5px 7px;letter-spacing:.06em}
  .mcard{padding:20px 18px 18px}
}
""".replace("%%MARK%%", MARK).replace("%%MARK_W%%", MARK_W)

# ---------------------------------------------------------------- JS
JS = r"""(function(){
var d=document,h=d.documentElement;
var show=h.getAttribute('data-mode')==='show';
/* header shadow */
var hd=d.querySelector('.hdr');
function sc(){if(hd)hd.classList.toggle('scrolled',window.pageYOffset>4);}
window.addEventListener('scroll',sc,{passive:true});sc();
/* mobile menu */
var mb=d.querySelector('.menu-btn'),nav=d.getElementById('nav');
function closeNav(){if(!mb)return;nav.classList.remove('open');mb.setAttribute('aria-expanded','false');mb.setAttribute('aria-label','Open menu');}
if(mb&&nav){
  mb.addEventListener('click',function(){var o=!nav.classList.contains('open');nav.classList.toggle('open',o);mb.setAttribute('aria-expanded',String(o));mb.setAttribute('aria-label',o?'Close menu':'Open menu');});
  nav.addEventListener('click',function(e){if(e.target.closest('a'))closeNav();});
  d.addEventListener('keydown',function(e){if(e.key==='Escape')closeNav();});
}
/* hidden door to the website editor: click the (c) symbol 5 times quickly */
var ck=d.querySelector('.cms-key'),cn=0,ct=0;
if(ck)ck.addEventListener('click',function(){var t=Date.now();cn=(t-ct<700)?cn+1:1;ct=t;if(cn>=5){cn=0;if(show){ck.title='The website editor opens here on the live site';}else{location.href='/studio/';}}});
/* year */
var y=d.querySelectorAll('[data-year]');for(var i=0;i<y.length;i++)y[i].textContent=new Date().getFullYear();
/* cookie notice: no tracking cookies are used; we only remember the visitor's choice */
var cb=d.getElementById('cookie');
if(cb){var seen=null;try{seen=localStorage.getItem('finlume-cookie-choice');}catch(e){}
  if(!seen)cb.hidden=false;
  cb.addEventListener('click',function(e){var b=e.target.closest('[data-cookie]');if(!b)return;try{localStorage.setItem('finlume-cookie-choice',b.getAttribute('data-cookie'));}catch(x){}cb.hidden=true;});}
/* showcase: one file, pages switched by #hash */
if(show){
  var views=d.querySelectorAll('.view');
  var route=function(){
    var id=(location.hash||'#home').slice(1),found=false;
    for(var i=0;i<views.length;i++){if(views[i].id==='v-'+id)found=true;}
    if(!found)id='home';
    for(var j=0;j<views.length;j++)views[j].hidden=views[j].id!=='v-'+id;
    var links=d.querySelectorAll('.nav-list a');
    for(var k=0;k<links.length;k++){if(links[k].getAttribute('href')==='#'+id)links[k].setAttribute('aria-current','page');else links[k].removeAttribute('aria-current');}
    window.scrollTo(0,0);
  };
  window.addEventListener('hashchange',route);route();
}
/* contact form */
var f=d.getElementById('contact-form');
if(f){
  var msg=d.getElementById('form-msg');
  var t0=Date.now();
  var ta=d.getElementById('f-message'),sel=d.getElementById('f-service'),touched=false;
  var defMsg=function(svc){return svc?"Hi Finlume, I'm interested in "+svc+". Please contact me to book a free consultation.":"Hi Finlume, I'd like to book a free consultation. Please contact me to discuss how you can help my business.";};
  if(ta){ta.addEventListener('input',function(){touched=true;});}
  if(sel&&ta){sel.addEventListener('change',function(){if(!touched)ta.value=defMsg(sel.value);});}
  var req=f.querySelectorAll('input:not([type=hidden]):not([name=bot-field]),select,textarea');
  var check=function(el){if(el.type!=='checkbox'&&el.tagName!=='SELECT')el.value=el.value.replace(/^\s+|\s+$/g,'');el.setCustomValidity('');if(el.minLength>0&&el.value&&el.value.length<el.minLength)el.setCustomValidity('short');var ok=el.checkValidity();el.setAttribute('aria-invalid',ok?'false':'true');var e=d.getElementById(el.id+'-err');
    if(e)e.textContent=ok?'':(el.type==='checkbox'?'Please tick this box so we can reply to you.':el.validity.valueMissing?'This field is required.':el.type==='email'?'Please enter a valid email address.':el.type==='tel'?'Please enter a valid phone number.':(el.validity.tooShort||el.validity.customError)?(el.name==='name'?'Please enter your full name.':'Please add a little more detail.'):'Please check this field.');return ok;};
  for(var r=0;r<req.length;r++){(function(el){el.addEventListener(el.type==='checkbox'?'change':'blur',function(){check(el);});})(req[r]);}
  f.addEventListener('submit',function(ev){
    var bad=[];for(var r=0;r<req.length;r++){if(!check(req[r]))bad.push(req[r]);}
    if(bad.length){ev.preventDefault();bad[0].focus();return;}
    var last=0;try{last=+localStorage.getItem('finlume-last-submit')||0;}catch(x){}
    if(Date.now()-last<60000){ev.preventDefault();msg.hidden=false;msg.className='form-msg bad';msg.textContent='Your previous message was sent a moment ago. Please wait a minute before sending another.';return;}
    if(ta&&!ta.value.replace(/\s/g,''))ta.value=defMsg(sel?sel.value:'');
    if(show){ev.preventDefault();msg.hidden=false;msg.className='form-msg ok';msg.textContent='Preview only: on the live website this message is delivered to Finlume through Netlify Forms.';return;}
    if(!window.fetch||!window.FormData||!window.URLSearchParams)return;
    ev.preventDefault();
    var btn=f.querySelector('[type=submit]');btn.disabled=true;var btnHtml=btn.innerHTML;btn.textContent='Sending…';
    msg.hidden=false;msg.className='form-msg ok';msg.textContent='Sending your message, this takes a few seconds…';
    var data={};new FormData(f).forEach(function(v,k){data[k]=v;});
    var wait=Math.max(0,3000-(Date.now()-t0)); /* bots submit instantly; people never notice this pause */
    new Promise(function(ok){setTimeout(ok,wait);}).then(function(){return fetch('/api/contact',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(data)});})
      .then(function(res){return res.json().then(function(j){if(!res.ok||!j.ok)throw new Error(res.status);});})
      .then(function(){try{localStorage.setItem('finlume-last-submit',String(Date.now()));}catch(x){}window.location.href='/thank-you';})
      .catch(function(){
        /* Fallback: if the form service is unavailable, send the same message by email or WhatsApp instead */
        btn.disabled=false;btn.innerHTML=btnHtml;
        if(f.elements['bot-field']&&f.elements['bot-field'].value)return;
        var v=function(n){var e=f.elements[n];return e&&e.value?e.value:'';};
        var body='Name: '+v('name')+'\nEmail: '+v('email')+'\nPhone: '+v('phone')+'\nCompany: '+v('company')+'\nService: '+v('service')+'\n\n'+v('message');
        var mail='mailto:'+f.getAttribute('data-to')+'?subject='+encodeURIComponent('Website enquiry from '+v('name'))+'&body='+encodeURIComponent(body);
        var wa='https://wa.me/'+f.getAttribute('data-wa')+'?text='+encodeURIComponent('Hi Finlume, website enquiry:\n\n'+body);
        msg.hidden=false;msg.className='form-msg ok';msg.textContent='';
        var p1=d.createElement('p');p1.textContent='Almost done: choose how to send your message. It is already filled in for you.';msg.appendChild(p1);
        var row=d.createElement('div');row.className='btn-row';
        var a1=d.createElement('a');a1.className='btn btn-navy';a1.href=mail;a1.textContent='Send by email';
        var a2=d.createElement('a');a2.className='btn btn-wa';a2.href=wa;a2.target='_blank';a2.rel='noopener noreferrer';a2.textContent='Send on WhatsApp';
        row.appendChild(a1);row.appendChild(a2);msg.appendChild(row);
        try{localStorage.removeItem('finlume-last-submit');}catch(x){}
      });
  });
}
})();"""

# ---------------------------------------------------------------- helpers
PAGES = [("home", "Home"), ("services", "Services"), ("about", "About Us"), ("contact", "Contact Us")]


class Ctx:
    def __init__(self, mode):
        self.mode = mode  # 'site' or 'show'

    def href(self, page, frag=None):
        if self.mode == "show":
            return "#" + page
        f = "/" if page == "home" else "/" + page
        return f + ("#" + frag if frag else "")


def sweep_svg(cls=""):
    return ('<svg class="sweep %s" viewBox="0 0 1440 640" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">'
            '<path class="s4" d="M-80 700 C 360 520 820 470 1520 120"/>'
            '<path class="s3 draw" d="M-80 610 C 300 470 700 450 1520 40"/>'
            '<path class="s1 draw" d="M-80 660 C 340 520 760 500 1520 170"/>'
            '<path class="s2 draw" d="M-80 720 C 400 590 860 560 1520 290"/>'
            '</svg>') % cls


def brand(light=False):
    sub = '<span class="brand-sub">BUSINESS SOLUTIONS (PTY) LTD</span>' if light else ""
    return ('<span class="brand-mark" aria-hidden="true"></span><span class="brand-txt"><span class="brand-name">FINLUME</span>'
            + sub + '</span>')


def header(c, active):
    items = "".join('<li><a href="%s"%s>%s</a></li>' % (c.href(p), ' aria-current="page"' if p == active else "", t) for p, t in PAGES)
    return ('<header class="hdr"><div class="wrap hdr-in">'
            '<a class="brand" href="%s">%s</a>'
            '<button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav" aria-label="Open menu"><span></span></button>'
            '<nav class="nav" id="nav" aria-label="Main"><ul class="nav-list">%s</ul>'
            '<a class="btn btn-navy" href="%s">Book a free consultation</a></nav>'
            '</div></header>') % (c.href("home"), brand(), items, c.href("contact"))


def footer(c):
    svc = "".join('<li><a href="%s">%s</a></li>' % (c.href("services", s["id"]), E(s["title"])) for s in SERVICES)
    pdf = '<li><a href="/Finlume-Company-Profile.pdf">Company profile (PDF)</a></li>' if c.mode == "site" else ""
    return ('<footer class="ftr"><div class="wrap"><div class="ftr-top">'
            '<div><a class="brand light" href="%s">%s</a>'
            '<p>@@settings.footer_about@@</p></div>'
            '<div><h2>Company</h2><ul><li><a href="%s">Home</a></li><li><a href="%s">Services</a></li><li><a href="%s">About Us</a></li>'
            '<li><a href="%s">Contact Us</a></li><li><a href="%s">Privacy Notice</a></li><li><a href="%s">Terms &amp; Conditions</a></li>%s</ul></div>'
            '<div><h2>Services</h2><ul>%s</ul></div>'
            '<div><h2>Get in touch</h2><ul class="ftr-c">'
            '<li>%s<a href="tel:%s">%s</a></li><li>%s<a href="%s" target="_blank" rel="noopener noreferrer">WhatsApp us</a></li>'
            '<li>%s<a href="mailto:%s">%s</a></li><li>%s<span>%s</span></li><li>%s<span>%s</span></li></ul></div>'
            '</div><div class="ftr-bot"><span><span class="cms-key" title="">©</span> <span data-year>2026</span> Finlume Business Solutions (Pty) Ltd · <span class="nw">Reg. No. %s</span> · All rights reserved.</span>'
            '<span class="tag">Clarity in every number</span></div></div></footer>'
            '<aside aria-label="Quick contact"><a class="wa" href="%s" target="_blank" rel="noopener noreferrer" aria-label="Chat with Finlume on WhatsApp">%s</a></aside>'
            '<div class="cookie" id="cookie" role="region" aria-label="Cookie notice" hidden><p><strong>Cookies.</strong> We don\'t use advertising or tracking cookies. '
            'This site only remembers your choice on this device. <a href="%s">Read our privacy notice</a></p>'
            '<div class="cookie-btns"><button class="btn btn-line" type="button" data-cookie="essential">Essential only</button>'
            '<button class="btn btn-navy" type="button" data-cookie="accepted">Accept</button></div></div>') % (
        c.href("home"), brand(True), c.href("home"), c.href("services"), c.href("about"), c.href("contact"), c.href("privacy"), c.href("terms"), pdf, svc,
        I["phone"], PHONE_TEL, PHONE_DISPLAY, I["whatsapp"], WA, I["mail"], EMAIL, EMAIL, I["clock"], HOURS, I["pin"], AREA, E(REG_NO), WA, I["whatsapp"], c.href("privacy", "cookies"))


def cta(c, title, text):
    return ('<section class="cta"><div class="wrap"><div class="cta-box"><span class="cta-mark" aria-hidden="true"></span>'
            '<div><h2>%s</h2><p>%s</p></div><a class="btn btn-gold" href="%s">Book a free consultation %s</a></div></div></section>') % (
        title, text, c.href("contact"), I["arrow"])


def checks(items):
    return '<ul class="checks">' + "".join("<li>%s<span>%s</span></li>" % (I["check"], E(x)) for x in items) + "</ul>"


def phero(eyebrow, title, lead, extra=""):
    return ('<section class="phero">%s<div class="wrap"><p class="eyebrow">%s</p><h1>%s</h1><p class="lead">%s</p>%s</div></section>') % (
        sweep_svg(), eyebrow, title, lead, extra)


# ---------------------------------------------------------------- pages
def _num(n):
    return ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"][n] if n <= 12 else str(n)


def page_home(c):
    svc_cards = "".join(
        '<article class="card"><span class="ico">%s</span><h3>%s</h3><p>%s</p><a class="more" href="%s">Learn more<span class="sr"> about %s</span>%s</a></article>' % (
            I[s["icon"]], E(s["title"]), E(s["short"]), c.href("services", s["id"]), E(s["title"]), I["arrow"]) for s in SERVICES)
    svc_cards += ('<article class="card feature"><h3>Not sure what you need?</h3><p>Tell us about your business and we\'ll recommend the right mix, with a clear fixed fee.</p>'
                  '<a class="btn btn-gold" href="%s">Book a free consultation</a></article>') % c.href("contact")
    dl = "".join('<li><span class="dl-when">%s</span><span class="dl-freq">%s</span><span class="dl-form">%s</span><p class="dl-what">%s</p></li>' % (
        E(a), E(b), E(f_), E(w)) for a, b, f_, w in DEADLINES)
    why = "".join('<div class="why-item"><span class="ico">%s</span><div><h3>%s</h3><p>%s</p></div></div>' % (I[i], E(t), E(x)) for i, t, x in WHY)
    cmp_rows = "".join('<div class="cmp-row" role="row"><span role="rowheader">%s</span><span role="cell" class="no">%s</span><span role="cell" class="yes">%s</span></div>' % (
        E(a), E(b), E(x)) for a, b, x in COMPARE)
    steps = "".join('<li class="step"><span class="step-n">%02d</span><h3>%s</h3><p>%s</p></li>' % (n + 1, E(t), E(x)) for n, (t, x) in enumerate(STEPS))
    serve = "".join('<li%s>%s<div><h3>%s</h3><p>%s</p></div></li>' % (' class="gold"' if n == len(SERVE) - 1 else "", I[i], E(t), E(x))
                    for n, (i, t, x) in enumerate(SERVE))
    faq = "".join('<details><summary>%s%s</summary><p>%s</p></details>' % (E(q), I["plus"], E(a)) for q, a in FAQ)
    if c.mode == "site":
        prof_btns = ('<a class="btn btn-navy" href="/Finlume-Company-Profile.pdf" download>Download the profile (PDF) %s</a>'
                     '<a class="btn btn-line" href="/Finlume-Company-Profile.pdf" target="_blank" rel="noopener">View online</a>') % I["download"]
    else:
        prof_btns = '<a class="btn btn-navy" href="#contact">Request the profile %s</a>' % I["arrow"]
    month = '<span class="mcard-month">Example month</span>'
    return """
<section class="hero">%s
  <div class="wrap hero-in">
    <div>
      <p class="eyebrow rise">@@home.hero_eyebrow@@</p>
      <h1 class="rise d2">@@home.hero_title@@ <span class="grad-word">@@home.hero_highlight@@</span></h1>
      <p class="lead rise d3">@@home.hero_lead@@</p>
      <div class="btn-row rise d3"><a class="btn btn-gold" href="%s">Book a free consultation %s</a><a class="btn btn-ghost" href="%s">Explore our services</a></div>
    </div>
    <div class="mcard rise d3" aria-label="Example of a Finlume month-end checklist">
      <div class="mcard-top"><p class="mcard-title">Month-end, handled</p>%s</div>
      <ul class="mlist">
        <li><span class="tick">%s</span><span class="lbl">Bank accounts reconciled</span><span class="pill ok">Done</span></li>
        <li><span class="tick">%s</span><span class="lbl">Payroll run &amp; EMP201 filed</span><span class="pill ok">Submitted</span></li>
        <li><span class="tick">%s</span><span class="lbl">VAT201 prepared</span><span class="pill wait">For approval</span></li>
        <li><span class="tick">%s</span><span class="lbl">Management pack &amp; review call</span><span class="pill ok">Sent</span></li>
      </ul>
      <p class="mcard-note">Illustration of the monthly checklist we run for every client.</p>
    </div>
  </div>
</section>
<section class="trust" aria-label="What you can expect"><div class="wrap"><ul>
  <li>%s Qualified oversight</li><li>%s SARS &amp; CIPC compliant</li><li>%s POPIA-conscious</li><li>%s Fixed monthly fees</li><li>%s Remote &amp; in person</li>
</ul></div></section>
<section class="sec"><div class="wrap split">
  <div><p class="eyebrow">@@home.intro_eyebrow@@</p><h2>@@home.intro_title@@</h2></div>
  <div class="txt">@@P:home.intro_text@@</div>
</div></section>
<section class="sec bg-paper" id="services"><div class="wrap">
  <div class="head c"><p class="eyebrow">Our services</p><h2>@@home.services_title@@</h2><p class="lead">@@home.services_lead@@</p></div>
  <div class="grid4">%s</div>
</div></section>
<section class="sec"><div class="wrap">
  <div class="head"><p class="eyebrow">The deadlines we watch for you</p><h2>@@home.deadlines_title@@</h2><p class="lead">@@home.deadlines_lead@@</p></div>
  <ul class="dl">%s</ul>
  <p class="fine">General SARS and CIPC rules. Your exact dates depend on your registrations, VAT category and financial year-end.</p>
</div></section>
<section class="sec bg-mist"><div class="wrap why-wrap">
  <div><div class="head"><p class="eyebrow">Why Finlume</p><h2>@@home.why_title@@</h2></div><div class="why">%s</div></div>
  <div class="cmp" role="table" aria-label="In-house finance team compared with Finlume"><p class="cmp-cap">In-house team vs Finlume</p>
    <div class="cmp-row cmp-head" role="row"><span role="columnheader"><span class="sr">Item</span></span><span role="columnheader">In-house</span><span role="columnheader">Finlume</span></div>%s</div>
</div></section>
<section class="sec"><div class="wrap">
  <div class="head c"><p class="eyebrow">How we work</p><h2>@@home.steps_title@@</h2></div>
  <ol class="steps">%s</ol>
</div></section>
<section class="sec dark">%s<div class="wrap">
  <div class="head c"><p class="eyebrow">Who we serve</p><h2>@@home.serve_title@@</h2><p class="lead">@@home.serve_lead@@</p></div>
  <ul class="serve">%s</ul>
</div></section>
<section class="sec"><div class="wrap faq-wrap">
  <div><p class="eyebrow">Questions &amp; answers</p><h2>Frequently asked questions</h2><p class="lead">Can't find your answer? <a href="%s">Ask us directly</a>.</p></div>
  <div class="faq">%s</div>
</div></section>
<section class="sec bg-paper"><div class="wrap prof">
  <div class="prof-img"><img src="%s" alt="Cover of the Finlume company profile" width="420" height="594" loading="lazy" decoding="async"></div>
  <div><p class="eyebrow">Company profile</p><h2>Get to know Finlume in eight pages</h2>
  <p class="lead">Our company profile covers who we are, our founder, our values and every service we offer. It is ideal to share with partners, directors or your board.</p>
  %s<div class="btn-row">%s</div></div>
</div></section>
%s
""" % (sweep_svg(), c.href("contact"), I["arrow"], c.href("services"), month, I["check"], I["check"], I["check"], I["check"],
       I["shield"], I["tax"], I["lock"], I["calendar"], I["pin"], svc_cards, dl, why, cmp_rows, steps, sweep_svg(), serve, c.href("contact"), faq,
       (COVER if c.mode == "show" else "/profile-cover.jpg"), checks(["Vision, mission and values", "Meet the founder, @@about.founder_name@@", "All %s services explained" % _num(len(SERVICES)), "How we work and who we serve"]),
       prof_btns, cta(c, "@@home.cta_title@@", "@@home.cta_text@@"))


def page_services(c):
    chips = '<div class="chips">' + "".join('<a href="%s">%s</a>' % ("#svc-" + s["id"] if c.mode == "site" else "#services", E(s["title"])) for s in SERVICES) + "</div>"
    blocks = "".join(
        '<article class="svc" id="svc-%s"><div><span class="svc-n">%02d / %02d</span><h2>%s</h2><p class="sum">%s</p><p>%s</p>'
        '<a class="more" href="%s">Ask about this service %s</a></div><div class="incl"><h3>What\'s included</h3>%s</div></article>' % (
            s["id"], n + 1, len(SERVICES), E(s["title"]), E(s["short"]), E(s["long"]), c.href("contact"), I["arrow"], checks(s["items"]))
        for n, s in enumerate(SERVICES))
    eng = "".join('<article class="card%s"><span class="svc-n">%s</span><h3>%s</h3><p>%s</p>%s<p class="best">%s</p></article>' % (
        " feature" if n == 2 else "", (["Ongoing", "Project", "On demand"] + ["Option"] * 20)[n], E(t), E(x), checks(items), E(best)) for n, (t, x, items, best) in enumerate(ENGAGEMENT))
    return phero("Our services", "@@services.hero_title@@", "@@services.hero_lead@@", chips) + """
<section class="sec"><div class="wrap">%s</div></section>
<section class="sec bg-paper"><div class="wrap">
  <div class="head c"><p class="eyebrow">Ways to work with us</p><h2>Flexible engagement models</h2><p class="lead">Every business is different. Choose the arrangement that suits you, and change it as you grow.</p></div>
  <div class="engage">%s</div>
</div></section>%s""" % (blocks, eng, cta(c, "@@services.cta_title@@", "@@services.cta_text@@"))


def page_about(c):
    vals = "".join('<div class="card"><span class="ico">%s</span><h3>%s</h3><p>%s</p></div>' % (I[i], E(t), E(x)) for i, t, x in VALUES)
    com = "".join('<div class="card"><span class="ico">%s</span><h3>%s</h3><p>%s</p></div>' % (I[i], E(t), E(x)) for i, t, x in COMMITMENTS)
    return phero("About Finlume", "@@about.hero_title@@", "@@about.hero_lead@@") + """
<section class="sec"><div class="wrap split">
  <div><p class="eyebrow">Our story</p><h2>@@about.story_title@@</h2></div>
  <div class="txt">@@P:about.story@@</div>
</div>
<div class="wrap">
  <div class="glance" aria-label="Finlume at a glance">
    <div><span class="g-k">Founded</span><span class="g-v">2026 · South Africa</span></div>
    <div><span class="g-k">Led by</span><span class="g-v">A qualified accountant</span></div>
    <div><span class="g-k">Services</span><span class="g-v">%d core finance services</span></div>
    <div><span class="g-k">Fees</span><span class="g-v">Fixed &amp; agreed upfront</span></div>
    <div><span class="g-k">Meetings</span><span class="g-v">Remote &amp; in person</span></div>
  </div>
  <p class="name"><b>Fin</b>ance + <b>lume</b>n <small>(light)</small>. We shed light on your numbers, so you always have <i>clarity in every number</i>.</p>
</div></section>
<section class="sec bg-paper"><div class="wrap founder">
  %s
  <div><p class="eyebrow">Meet the founder</p><h2>@@about.founder_name@@</h2><p class="f-role">@@about.founder_role@@</p>
  @@P:about.founder_bio@@
  <blockquote class="quote"><p>“@@about.founder_quote@@”</p><cite>@@about.founder_name@@</cite></blockquote></div>
</div></section>
<section class="sec"><div class="wrap vm">
  <div class="d"><p class="eyebrow">Our vision</p><h2>Where we're going</h2><p>@@about.vision@@</p></div>
  <div><p class="eyebrow">Our mission</p><h2>How we get there</h2><p>@@about.mission@@</p></div>
</div></section>
<section class="sec bg-mist"><div class="wrap">
  <div class="head c"><p class="eyebrow">Our values</p><h2>What we stand for</h2></div>
  <div class="values">%s</div>
</div></section>
<section class="sec"><div class="wrap">
  <div class="head c"><p class="eyebrow">Our promise</p><h2>Our commitments to you</h2><p class="lead">What you can expect from the day you start working with Finlume.</p></div>
  <div class="grid4">%s</div>
</div></section>%s""" % (len(SERVICES), founder_photo(), vals, com, cta(c, "@@about.cta_title@@", "@@about.cta_text@@"))


def page_contact(c):
    opts = "".join('<option>%s</option>' % E(s["title"]) for s in SERVICES) + "<option>Not sure yet</option>"
    netlify = ""  # handled by the Netlify Function /api/contact (functions/contact.mjs)
    return phero("Contact us", "@@contact.hero_title@@", "@@contact.hero_lead@@") + """
<section class="sec bg-paper"><div class="wrap contact">
  <div class="cards">
    <a class="cc" href="tel:%s">%s<span><span class="k">Call us</span><span class="v">%s</span></span></a>
    <a class="cc" href="%s" target="_blank" rel="noopener noreferrer">%s<span><span class="k">WhatsApp</span><span class="v">%s</span></span></a>
    <a class="cc" href="mailto:%s">%s<span><span class="k">Email</span><span class="v">%s</span></span></a>
    <div class="cc">%s<span><span class="k">Office hours</span><span class="v">%s</span></span></div>
    <div class="cc">%s<span><span class="k">Area served</span><span class="v">%s</span></span></div>
    <div class="wa-card"><p class="wa-h">Prefer to chat?</p><p>Send us a message on WhatsApp and we'll respond during office hours.</p><a class="btn btn-wa" href="%s" target="_blank" rel="noopener noreferrer">%s Chat on WhatsApp</a></div>
  </div>
  <form class="form" id="contact-form" name="contact" method="POST" action="/api/contact" data-to="%s" data-wa="%s"%s novalidate>
    <h2>Send us a message</h2><p class="lead">Tell us a little about your business and how we can help. Fields marked * are required.</p>
    <p class="hp" aria-hidden="true"><label for="f-bot">Leave this empty</label><input id="f-bot" name="bot-field" tabindex="-1" autocomplete="off" maxlength="50"></p>
    <div class="fgrid">
      <div class="field"><label for="f-name">Full name *</label><input id="f-name" name="name" type="text" autocomplete="name" minlength="2" maxlength="100" required aria-describedby="f-name-err"><span class="err" id="f-name-err" aria-live="polite"></span></div>
      <div class="field"><label for="f-email">Email address *</label><input id="f-email" name="email" type="email" autocomplete="email" maxlength="150" pattern=".+@.+[.][a-zA-Z]{2,}" required aria-describedby="f-email-err"><span class="err" id="f-email-err" aria-live="polite"></span></div>
      <div class="field"><label for="f-phone">Phone number</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" maxlength="25" inputmode="tel" pattern="[+]?[0-9 ]{7,22}" title="Digits and spaces, optionally starting with +" aria-describedby="f-phone-err"><span class="err" id="f-phone-err" aria-live="polite"></span></div>
      <div class="field"><label for="f-company">Company name</label><input id="f-company" name="company" type="text" autocomplete="organization" maxlength="120"></div>
      <div class="field full"><label for="f-service">Service of interest</label><select id="f-service" name="service"><option value="">Select a service…</option>%s</select></div>
      <div class="field full"><label for="f-message">How can we help?</label><textarea id="f-message" name="message" maxlength="3000" aria-describedby="f-message-hint">Hi Finlume, I&#39;d like to book a free consultation. Please contact me to discuss how you can help my business.</textarea><span class="hint" id="f-message-hint">We've written a message for you. Send it as it is, or add your own details.</span></div>
      <div class="field full"><label class="consent" for="f-consent"><input id="f-consent" type="checkbox" name="consent" value="Yes" required aria-describedby="f-consent-err"><span>I agree that Finlume may use this information to respond to my enquiry, as described in the <a href="%s">Privacy Notice</a>. *</span></label><span class="err" id="f-consent-err" aria-live="polite"></span></div>
    </div>
    <div class="btn-row"><button class="btn btn-navy" type="submit">Send message %s</button></div>
    <p class="form-msg" id="form-msg" role="status" hidden></p>
  </form>
</div></section>""" % (PHONE_TEL, I["phone"], PHONE_DISPLAY, WA, I["whatsapp"], PHONE_DISPLAY, EMAIL, I["mail"], EMAIL, I["clock"], HOURS, I["pin"], AREA,
       WA, I["whatsapp"], FORM_TO, WA_NUMBER, netlify, opts, c.href("privacy"), I["arrow"])


def page_privacy(c):
    return phero("POPIA", "Privacy Notice", "How we collect, use and protect your personal information.") + """
<section class="sec"><div class="wrap"><div class="prose">
<p><em>Last updated: November 2026</em></p>
<h2>1. Who we are</h2><p>Finlume Business Solutions (Pty) Ltd ("Finlume", "we", "us") respects your privacy. This notice explains how we handle personal information in line with the Protection of Personal Information Act 4 of 2013 (POPIA). It applies to visitors to this website, people who contact us, and the clients for whom we provide services.</p>
<h2>2. Information Officer</h2><p>Our Information Officer is Rochelle Brandon, Founder &amp; Director. Contact: %s or %s.</p>
<h2>3. Information we collect</h2><ul><li>Contact details you give us, such as your name, email address, phone number and company name.</li><li>Information needed to deliver our services, such as identity and registration numbers, tax reference numbers, banking, financial records and payroll information.</li><li>Basic technical information that our website host records automatically for security and performance.</li></ul><p>This website does not use advertising or tracking cookies.</p>
<h2>4. How we use it</h2><ul><li>To respond to enquiries and prepare proposals.</li><li>To provide bookkeeping, payroll, tax, financial statement, advisory and secretarial services.</li><li>To submit returns and filings to authorities such as SARS and the CIPC on your instruction.</li><li>To meet our legal, regulatory and professional obligations.</li></ul><p>We only send marketing messages if you have agreed to receive them, and you can opt out at any time.</p>
<h2>5. Sharing</h2><p>We never sell personal information. We share it only where necessary: with authorities such as SARS and the CIPC when submitting on your behalf, with trusted professional partners such as independent reviewers when you ask us to, and with service providers that help us operate (for example cloud accounting software, email, and website hosting, including Netlify, which passes contact-form messages securely to our own mailbox). They must keep your information confidential and secure.</p>
<h2>6. Cross-border storage</h2><p>Some cloud services we use may store information on servers outside South Africa. When this happens we take reasonable steps to ensure it is protected to a standard comparable to POPIA.</p>
<h2>7. Security and retention</h2><p>We use appropriate technical and organisational measures, including access controls, encrypted connections and strict confidentiality. We keep information only as long as needed for its purpose or as required by law (for example, the Tax Administration Act and the Companies Act), then securely delete or destroy it.</p>
<h2>8. Your rights</h2><ul><li>Ask whether we hold your personal information and request a copy.</li><li>Ask us to correct or delete information that is inaccurate, out of date or unlawfully held.</li><li>Object to processing and withdraw consent where processing is based on consent.</li><li>Lodge a complaint with the Information Regulator (South Africa) at www.inforegulator.org.za.</li></ul>
<h2 id="cookies">9. Cookies</h2><p>This website does not use advertising, analytics or tracking cookies. When you choose an option in the cookie notice, your browser remembers that choice on your device so the notice is not shown again. The contact form stores a short timestamp on your device to prevent repeated submissions. Netlify, our website host, may set strictly necessary security cookies to protect the site.</p>
<h2>10. Changes</h2><p>We may update this notice from time to time. The latest version will always be on this page.</p>
</div></div></section>""" % (EMAIL, PHONE_DISPLAY)


def page_thanks(c):
    return """<section class="center"><div class="wrap"><div class="tick-big">%s</div><p class="eyebrow">Message sent</p><h1>Thank you for getting in touch</h1>
<p class="lead">We've received your message and will get back to you as soon as we can. If your matter is urgent, WhatsApp us or call %s.</p>
<div class="btn-row"><a class="btn btn-navy" href="%s">Back to home</a><a class="btn btn-line" href="%s" target="_blank" rel="noopener noreferrer">WhatsApp us</a></div></div></section>""" % (
        I["check"], PHONE_DISPLAY, c.href("home"), WA)


def page_404(c):
    return """<section class="center"><div class="wrap"><p class="big-n">404</p><h1>This page doesn't add up.</h1>
<p class="lead">The page you're looking for may have moved or no longer exists.</p>
<div class="btn-row"><a class="btn btn-navy" href="%s">Back to home</a><a class="btn btn-line" href="%s">Our services</a><a class="btn btn-line" href="%s">Contact us</a></div></div></section>""" % (
        c.href("home"), c.href("services"), c.href("contact"))


def page_terms(c):
    company = '<li>Name: Finlume Business Solutions (Pty) Ltd, a private company incorporated in South Africa</li>'
    if REG_NO:
        company += '<li>Registration number: %s</li>' % E(REG_NO)
    if PHYSICAL_ADDRESS:
        company += '<li>Physical address: %s</li>' % E(PHYSICAL_ADDRESS)
    company += '<li>Director: Rochelle Brandon</li><li>Phone / WhatsApp: %s</li><li>Email: %s</li><li>Website: www.finlume.co.za</li>' % (PHONE_DISPLAY, EMAIL)
    return phero("Legal", "Terms &amp; Conditions", "The terms that apply when you use this website or engage Finlume.") + """
<section class="sec"><div class="wrap"><div class="prose">
<p><em>Last updated: November 2026</em></p>
<h2>1. About these terms</h2><p>These terms apply to your use of www.finlume.co.za and to enquiries made through it. By using the website you agree to them. If you do not agree, please do not use the website.</p>
<h2>2. Company information</h2><ul>%s</ul>
<h2>3. Information on this website</h2><p>The content on this website is general information about our services. It is not professional, tax, accounting or legal advice for your specific situation. Tax law and deadlines change; please contact us before acting on any information here.</p>
<h2>4. Our services</h2><p>Services are provided only once we have agreed a written proposal or engagement letter with you. That document sets out the scope of work, responsibilities, fees and timelines, and it takes precedence over this website if there is any difference.</p>
<h2>5. Your responsibilities as a client</h2><ul><li>Provide complete, accurate and timely information and records.</li><li>Review and approve returns and statements before we submit them.</li><li>Tell us promptly about changes to your business, employees or registrations.</li></ul><p>You remain legally responsible for your tax affairs and company filings; we act on your instructions and the information you provide.</p>
<h2>6. Fees and payment</h2><p>Fees are as set out in your proposal. Ongoing services are billed as a fixed monthly fee and once-off work is quoted upfront. Fees for work outside the agreed scope are agreed with you before the work starts.</p>
<h2>7. Confidentiality and personal information</h2><p>We keep your information confidential and process personal information in line with POPIA, as explained in our <a href="%s">Privacy Notice</a>.</p>
<h2>8. Intellectual property</h2><p>The Finlume name, logo, website design and content belong to Finlume Business Solutions (Pty) Ltd. You may not copy or reuse them without our written permission.</p>
<h2>9. Limitation of liability</h2><p>To the extent permitted by law, including the Consumer Protection Act where it applies, Finlume is not liable for any loss arising from use of this website or reliance on its general content. Our liability for services is set out in your engagement letter.</p>
<h2>10. Links to other websites</h2><p>This website links to services such as WhatsApp. We are not responsible for the content or privacy practices of other websites.</p>
<h2>11. Website security</h2><p>You may not attempt to gain unauthorised access to this website, interfere with its operation, or send automated or bulk messages through its forms.</p>
<h2>12. Changes and governing law</h2><p>We may update these terms from time to time; the latest version will always be on this page. These terms are governed by the laws of the Republic of South Africa.</p>
<h2>13. Contact</h2><p>Questions about these terms? Email %s or call %s.</p>
</div></div></section>""" % (company, c.href("privacy"), EMAIL, PHONE_DISPLAY)


META = {
    "home": ("Finlume | Outsourced Accounting & Tax in South Africa", "Finlume is your external finance department: bookkeeping, payroll, tax and SARS compliance, annual financial statements and advisory for South African businesses."),
    "services": ("Services | Finlume Business Solutions", "Bookkeeping, payroll, tax and SARS compliance, annual financial statements, management accounts, business advisory and CIPC services."),
    "about": ("About Us | Finlume Business Solutions", "Meet Finlume, a founder-led South African outsourced accounting firm led by qualified accountant Rochelle Brandon."),
    "contact": ("Contact Us | Finlume Business Solutions", "Book a free consultation with Finlume. Call or WhatsApp +27 71 608 3460 or email info@finlume.co.za."),
    "terms": ("Terms & Conditions | Finlume Business Solutions", "The terms that apply when you use the Finlume website or engage Finlume Business Solutions for accounting, tax and advisory services."),
    "privacy": ("Privacy Notice | Finlume Business Solutions", "How Finlume collects, uses and protects personal information under POPIA."),
    "thank-you": ("Thank you | Finlume Business Solutions", "Thank you for contacting Finlume."),
    "404": ("Page not found | Finlume Business Solutions", "This page could not be found."),
}
BUILDERS = {"home": page_home, "services": page_services, "about": page_about, "contact": page_contact,
            "privacy": page_privacy, "terms": page_terms, "thank-you": page_thanks, "404": page_404}


def sha(s):
    return "'sha256-%s'" % base64.b64encode(hashlib.sha256(s.encode()).digest()).decode()


HEADJS = "document.documentElement.classList.add('js');"
CSP = ("default-src 'self'; script-src %s %s; style-src %s; img-src 'self' data:; font-src data:; connect-src 'self'; "
       "form-action 'self'; base-uri 'self'; object-src 'none'; frame-src 'none'") % (sha(HEADJS), sha(JS), sha(CSS))

# The strict, fingerprint-based policy lives in each page's own <meta> tag, so it always
# matches that page. The Netlify header adds the rules a <meta> tag cannot carry; it never
# needs updating when page content changes. Browsers enforce BOTH policies together.
HEADER_CSP = ("default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
              "font-src 'self' data:; connect-src 'self'; form-action 'self'; base-uri 'self'; object-src 'none'; frame-src 'none'")

LDJSON = ('{"@context":"https://schema.org","@type":"AccountingService","name":"Finlume Business Solutions (Pty) Ltd","alternateName":"Finlume",'
          '"slogan":"Clarity in every number","url":"%s/","telephone":"%s","email":"%s","areaServed":{"@type":"Country","name":"South Africa"},'
          '"address":{"@type":"PostalAddress","streetAddress":"38 Willow Green, 471 Furrow Road","addressLocality":"Equestria","addressRegion":"Gauteng","postalCode":"0181","addressCountry":"ZA"},"founder":{"@type":"Person","name":"Rochelle Brandon","jobTitle":"Founder & Director"},"openingHours":"Mo-Fr 08:00-17:00"}') % (DOMAIN, PHONE_TEL, EMAIL)


# ---------------------------------------------------------------- editable text (content/*.json)
import re as _re


def _val(key):
    sec, _, name = key.partition(".")
    v = TEXT.get(sec, {}).get(name, "")
    return "" if v is None else str(v).strip()


def fill(s):
    """Swap @@section.field@@ markers for the text saved by the website editor."""
    def rep(m):
        key = m.group(2)
        if m.group(1):  # paragraphs: blank lines start a new paragraph
            paras = [p.strip() for p in _re.split(r"\n\s*\n", _val(key)) if p.strip()]
            return "\n".join("<p>%s</p>" % E(p).replace("\n", "<br>") for p in paras)
        return E(_val(key))
    return _re.sub(r"@@(P:)?([a-z_]+\.[a-z_]+)@@", rep, s)


def founder_photo():
    name = _val("about.founder_name") or "Founder"
    photo = _val("about.founder_photo")
    if photo:
        if not photo.startswith(("/", "http")):
            photo = "/" + photo
        return ('<div class="f-photo has-img"><img src="%s" alt="Photo of %s" width="420" height="504" loading="lazy" decoding="async"></div>'
                % (E(photo), E(name)))
    initials = "".join(w[0] for w in name.split()[:2]).upper()
    return '<div class="f-photo" role="img" aria-label="Photo placeholder for %s"><span class="f-init">%s</span></div>' % (E(name), E(initials))



def build_site():
    out = os.path.join(HERE, "dist")
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    c = Ctx("site")
    for key, fn in BUILDERS.items():
        title, desc = META[key]
        fname = "index.html" if key == "home" else key + ".html"
        url = DOMAIN + "/" + ("" if key == "home" else key)
        active = key if key in dict(PAGES) else None
        robots = '<meta name="robots" content="noindex">' if key in ("404", "thank-you") else ""
        doc = """<!doctype html>
<html lang="en-ZA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="%s">
<title>%s</title>
<meta name="description" content="%s">
%s<link rel="canonical" href="%s">
<meta name="theme-color" content="#0B1F4B">
<meta name="format-detection" content="telephone=no">
<meta property="og:type" content="website"><meta property="og:site_name" content="Finlume Business Solutions"><meta property="og:locale" content="en_ZA">
<meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s">
<meta property="og:image" content="%s/og-image.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Finlume Business Solutions, Clarity in every number">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="%s"><meta name="twitter:description" content="%s"><meta name="twitter:image" content="%s/og-image.jpg">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<style>%s</style>
<script>%s</script>
<script type="application/ld+json">%s</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
%s
<main id="main">%s</main>
%s
<script>%s</script>
</body>
</html>
""" % (CSP, E(title), E(desc), robots, url, E(title), E(desc), url, DOMAIN, E(title), E(desc), DOMAIN, CSS, HEADJS, LDJSON, header(c, active), fill(fn(c)), fill(footer(c)), JS)
        with open(os.path.join(out, fname), "w", encoding="utf-8") as f:
            f.write(doc)
    # extra files (all at the top level, no folders)
    shutil.copy(os.path.join(HERE, "apple-touch-icon.png"), out)
    for fn_ in ("og-image.jpg", "favicon.ico", "favicon-32.png", "profile-cover.jpg", "finlume-email-logo.png"):
        shutil.copy(os.path.join(HERE, fn_), os.path.join(out, fn_))
    shutil.copy(os.path.join(HERE, "Finlume-Company-Profile.pdf"), os.path.join(out, "Finlume-Company-Profile.pdf"))
    with open(os.path.join(out, "robots.txt"), "w") as f:
        f.write("User-agent: *\nAllow: /\nDisallow: /thank-you\nDisallow: /thank-you.html\nDisallow: /404.html\n\nSitemap: %s/sitemap.xml\n" % DOMAIN)
    urls = ["", "services", "about", "contact", "privacy", "terms"]
    import datetime
    today = datetime.date.today().isoformat()
    with open(os.path.join(out, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                "".join("  <url><loc>%s/%s</loc><lastmod>%s</lastmod></url>\n" % (DOMAIN, u, today) for u in urls) + "</urlset>\n")
    with open(os.path.join(out, "security.txt"), "w") as f:
        f.write("Contact: mailto:%s\nExpires: 2027-10-31T00:00:00.000Z\nPreferred-Languages: en\n" % EMAIL)
    # pictures uploaded in the website editor
    up = os.path.join(HERE, "uploads")
    if os.path.isdir(up):
        shutil.copytree(up, os.path.join(out, "uploads"), ignore=shutil.ignore_patterns(".gitkeep"))
    build_studio(out)
    # Netlify settings live next to build.py (repo root); keep that file in step with this script
    with open(os.path.join(HERE, "netlify.toml"), "w") as f:
        f.write(NETLIFY_TOML)
    return out


# ---------------------------------------------------------------- website editor (Decap CMS) at /studio/
DECAP_JS = "decap-cms-3.17.1.js"  # stored in studio/, served from this site (no outside script)


def _repo():
    """GitHub repo of this site, e.g. "owner/name". Netlify provides REPOSITORY_URL during builds."""
    url = os.environ.get("REPOSITORY_URL", "")
    m = _re.search(r"github\.com[:/]+([^/]+/[^/]+?)(?:\.git)?/?$", url)
    return m.group(1) if m else os.environ.get("CMS_REPO", "OWNER/REPOSITORY")


def _yaml(v, ind=0):
    sp = "  " * ind
    if isinstance(v, dict):
        out = ""
        for k, x in v.items():
            if isinstance(x, (dict, list)) and x:
                out += "%s%s:\n%s" % (sp, k, _yaml(x, ind + 1))
            else:
                out += "%s%s: %s\n" % (sp, k, _yaml(x))
        return out
    if isinstance(v, list):
        out = ""
        for x in v:
            if isinstance(x, dict):
                body = _yaml(x, ind + 1)
                out += sp + "- " + body[len(sp) + 2:]
            else:
                out += "%s- %s\n" % (sp, _yaml(x))
        return out
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    return json_str(v)


def json_str(s):
    import json
    return json.dumps(s, ensure_ascii=False)


def F(name, label, widget="string", hint=None, **kw):
    d = {"name": name, "label": label, "widget": widget}
    if hint:
        d["hint"] = hint
    d.update(kw)
    return d


def cms_config():
    icons = sorted(ICONS.keys())
    ICON = F("icon", "Icon", "select", options=icons, default="check")
    card = lambda name, label, hint=None: F(name, label, "list", hint, collapsed=True, summary="{{fields.title}}",
                                            fields=[ICON, F("title", "Heading"), F("text", "Text", "text")])
    strings = lambda name, label, hint=None: F(name, label, "list", hint, field=F("item", "Item"))
    para = "Leave an empty line between paragraphs."
    settings = [
        F("phone_display", "Phone number (as shown)", hint="For example +27 71 608 3460"),
        F("phone_tel", "Phone number (for the call button)", hint="No spaces, for example +27716083460"),
        F("whatsapp_number", "WhatsApp number", hint="Country code and number, digits only, for example 27716083460"),
        F("whatsapp_text", "WhatsApp starting message"),
        F("email", "Email address"),
        F("hours", "Office hours"),
        F("area", "Area served"),
        F("reg_no", "Company registration number"),
        F("address", "Physical address"),
        F("footer_about", "Footer description", "text"),
    ]
    home = [
        F("hero_eyebrow", "Top banner: small heading"),
        F("hero_title", "Top banner: main heading"),
        F("hero_highlight", "Top banner: highlighted words", hint="Shown in the gold gradient after the main heading"),
        F("hero_lead", "Top banner: intro text", "text"),
        F("intro_eyebrow", "Intro: small heading"),
        F("intro_title", "Intro: heading"),
        F("intro_text", "Intro: text", "text", para),
        F("services_title", "Services section: heading"),
        F("services_lead", "Services section: intro", "text", "The service cards themselves are edited under Services page."),
        F("deadlines_title", "Deadlines: heading"),
        F("deadlines_lead", "Deadlines: intro", "text"),
        F("deadlines", "Deadlines", "list", collapsed=True, summary="{{fields.form}}", fields=[
            F("when", "When"), F("often", "How often"), F("form", "Form name"), F("what", "What it is", "text")]),
        F("why_title", "Why Finlume: heading"),
        card("why", "Why Finlume: reasons"),
        F("compare", "In-house vs Finlume table", "list", collapsed=True, summary="{{fields.item}}", fields=[
            F("item", "Row"), F("inhouse", "In-house"), F("finlume", "Finlume")]),
        F("steps_title", "How we work: heading"),
        F("steps", "How we work: steps", "list", collapsed=True, summary="{{fields.title}}", fields=[F("title", "Step"), F("text", "Text", "text")]),
        F("serve_title", "Who we serve: heading"),
        F("serve_lead", "Who we serve: intro", "text"),
        card("serve", "Who we serve: groups"),
        F("faq", "Frequently asked questions", "list", collapsed=True, summary="{{fields.question}}", fields=[
            F("question", "Question"), F("answer", "Answer", "text")]),
        F("cta_title", "Bottom banner: heading"),
        F("cta_text", "Bottom banner: text", "text"),
    ]
    services = [
        F("hero_title", "Top banner: heading"),
        F("hero_lead", "Top banner: intro", "text"),
        F("services", "Services", "list", "Drag to change the order. These also appear on the Home page, in the footer and in the contact form.",
          collapsed=True, summary="{{fields.title}}", fields=[
              F("title", "Service name"), ICON,
              F("short", "Short description", "text", "Shown on the Home page card"),
              F("long", "Full description", "text"),
              strings("items", "What's included"),
              F("id", "Link name", required=False, hint="Optional. Lowercase with dashes, used in the page address. Leave empty to make one from the name.")]),
        F("engagement", "Ways to work with us", "list", collapsed=True, summary="{{fields.title}}", fields=[
            F("title", "Heading"), F("text", "Text", "text"), strings("items", "Points"), F("best", "Best for")]),
        F("cta_title", "Bottom banner: heading"),
        F("cta_text", "Bottom banner: text", "text"),
    ]
    about = [
        F("hero_title", "Top banner: heading"),
        F("hero_lead", "Top banner: intro", "text"),
        F("story_title", "Our story: heading"),
        F("story", "Our story: text", "text", para),
        F("founder_name", "Founder: name"),
        F("founder_role", "Founder: role"),
        F("founder_photo", "Founder: photo", "image", "Portrait photo, ideally under 500 KB. Leave empty to show the initials.", required=False),
        F("founder_bio", "Founder: about", "text", para),
        F("founder_quote", "Founder: quote", "text"),
        F("vision", "Vision", "text"),
        F("mission", "Mission", "text"),
        card("values", "Values"),
        card("commitments", "Commitments"),
        F("cta_title", "Bottom banner: heading"),
        F("cta_text", "Bottom banner: text", "text"),
    ]
    contact = [F("hero_title", "Top banner: heading"), F("hero_lead", "Top banner: intro", "text")]
    page = lambda name, label, fields, desc=None: dict(name=name, label=label, file="content/%s.json" % name, fields=fields, **({"description": desc} if desc else {}))
    return {
        "backend": {"name": "github", "repo": _repo(), "branch": os.environ.get("CMS_BRANCH", "main"),
                    "api_root": "/api/gh",  # through this site's own sign-in relay (netlify/functions/cms-github.mjs)
                    "commit_messages": {"update": "Website editor: update {{slug}}", "uploadMedia": "Website editor: upload {{path}}",
                                        "deleteMedia": "Website editor: delete {{path}}"}},
        "site_url": DOMAIN, "display_url": DOMAIN, "logo_url": "/apple-touch-icon.png",
        "media_folder": "uploads", "public_folder": "/uploads",
        "collections": [{
            "name": "pages", "label": "Website", "editor": {"preview": False},
            "description": "Edit a page, then click Publish. The live website updates about one minute later.",
            "files": [
                page("home", "Home page", home),
                page("services", "Services page", services),
                page("about", "About page", about),
                page("contact", "Contact page", contact),
                page("settings", "Contact details & footer", settings, "Phone, email, WhatsApp and company details used across the whole website."),
            ]}],
    }


def build_studio(out):
    d = os.path.join(out, "studio")
    os.makedirs(d, exist_ok=True)
    shutil.copy(os.path.join(HERE, "studio", DECAP_JS), os.path.join(d, DECAP_JS))
    with open(os.path.join(d, "config.yml"), "w", encoding="utf-8") as f:
        f.write("# Website editor settings, generated by build.py (edit build.py, not this file)\n" + _yaml(cms_config()))
    shutil.copy(os.path.join(HERE, "studio", "login.js"), os.path.join(d, "login.js"))
    mark = b64(os.path.join(HERE, "mark.png"), "image/png")
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(STUDIO_HTML.replace("%%MARK%%", mark))


STUDIO_HTML = """<!doctype html>
<html lang="en-ZA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Finlume website editor</title>
<link rel="icon" href="/favicon.ico">
<link href="/studio/config.yml" type="text/yaml" rel="cms-config-url">
<style>
body{margin:0}
#login{min-height:100vh;display:grid;place-items:center;padding:24px;background:linear-gradient(140deg,#081839,#0B1F4B 45%,#174091);font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
#login[hidden]{display:none}
.lbox{width:100%;max-width:380px;background:#fff;border-radius:18px;padding:34px 30px;box-shadow:0 24px 60px rgba(0,0,0,.35)}
.lbox img{width:52px;height:auto;display:block;margin:0 auto 12px}
.lbox h1{font-size:1.3rem;margin:0 0 4px;text-align:center;color:#0B1F4B}
.lbox p.sub{margin:0 0 22px;text-align:center;color:#5B6478;font-size:.92rem}
.lbox label{display:block;font-size:.85rem;font-weight:600;color:#0B1F4B;margin:14px 0 6px}
.lbox input{width:100%;box-sizing:border-box;padding:12px 14px;border:1.5px solid #CBD3E1;border-radius:10px;font-size:1rem}
.lbox input:focus{outline:none;border-color:#1E5BB0;box-shadow:0 0 0 3px rgba(30,91,176,.18)}
.lbox button{width:100%;margin-top:22px;padding:13px;border:0;border-radius:10px;background:#0B1F4B;color:#fff;font-size:1rem;font-weight:600;cursor:pointer}
.lbox button:hover{background:#163C8F}.lbox button:disabled{opacity:.7;cursor:wait}
#login-msg{min-height:1.3em;margin:14px 0 0;color:#B42318;font-size:.9rem;text-align:center}
.lbox a{display:block;text-align:center;margin-top:18px;color:#5B6478;font-size:.85rem}
</style>
</head>
<body>
<main id="login" hidden>
  <form class="lbox" id="login-form" autocomplete="on" novalidate>
    <img src="%%MARK%%" alt="" width="52" height="52">
    <h1>Website editor</h1>
    <p class="sub">Finlume Business Solutions</p>
    <label for="u">Username</label>
    <input id="u" name="username" autocomplete="username" autocapitalize="none" spellcheck="false" maxlength="100" required>
    <label for="p">Password</label>
    <input id="p" name="password" type="password" autocomplete="current-password" maxlength="200" required>
    <button type="submit">Sign in</button>
    <p id="login-msg" role="alert"></p>
    <a href="/">Back to the website</a>
  </form>
</main>
<script src="/studio/login.js"></script>
</body>
</html>
"""


NETLIFY_TOML = """# Finlume website, Netlify settings (generated by build.py, edit build.py rather than this file).
# Netlify runs build.py, which turns the text in content/*.json into the finished pages in dist/.
[build]
  command = "python3 build.py"
  publish = "dist"
  functions = "netlify/functions"

# Only SMTP_PASS is a real secret. These other settings are public information that also
# appears on the website (business name, email addresses), so Netlify's secret scanner must
# not treat them as leaked secrets.
[build.environment]
  SECRETS_SCAN_OMIT_KEYS = "FORM_SITE_NAME,SMTP_USER,MAIL_TO,SMTP_HOST,SMTP_PORT,CMS_USERNAME"

# Friendly addresses
[[redirects]]
  from = "/about"
  to = "/about.html"
  status = 200
[[redirects]]
  from = "/services"
  to = "/services.html"
  status = 200
[[redirects]]
  from = "/contact"
  to = "/contact.html"
  status = 200
  # Rate limit on the contact page: max 30 requests per minute from one IP address
  [redirects.rate_limit]
  window_limit = 30
  window_size = 60
  aggregate_by = ["ip", "domain"]
[[redirects]]
  from = "/privacy"
  to = "/privacy.html"
  status = 200
[[redirects]]
  from = "/terms"
  to = "/terms.html"
  status = 200
[[redirects]]
  from = "/profile"
  to = "/Finlume-Company-Profile.pdf"
  status = 301
[[redirects]]
  from = "/.well-known/security.txt"
  to = "/security.txt"
  status = 200

# Website editor: /studio/ (opened by clicking the © symbol 5 times). Netlify serves studio/index.html there.

# Block common hacking probes (this site has no PHP or database; the editor lives at /studio/)
[[redirects]]
  from = "/wp-admin/*"
  to = "/404.html"
  status = 404
  force = true
[[redirects]]
  from = "/wp-login.php"
  to = "/404.html"
  status = 404
  force = true
[[redirects]]
  from = "/xmlrpc.php"
  to = "/404.html"
  status = 404
  force = true
[[redirects]]
  from = "/.env"
  to = "/404.html"
  status = 404
  force = true
[[redirects]]
  from = "/.git/*"
  to = "/404.html"
  status = 404
  force = true
[[redirects]]
  from = "/admin/*"
  to = "/404.html"
  status = 404
  force = true
[[redirects]]
  from = "/phpmyadmin/*"
  to = "/404.html"
  status = 404
  force = true
[[redirects]]
  from = "/netlify/*"
  to = "/404.html"
  status = 404
  force = true
[[redirects]]
  from = "/README.md"
  to = "/404.html"
  status = 404
  force = true
[[redirects]]
  from = "/netlify.toml"
  to = "/404.html"
  status = 404
  force = true

# Security headers. Every page carries its own strict Content-Security-Policy in a <meta> tag
# (fingerprinted scripts only). The editor gets its own policy below.
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    Permissions-Policy = "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
    Strict-Transport-Security = "max-age=63072000; includeSubDomains"
    Cross-Origin-Opener-Policy = "same-origin"
    X-Permitted-Cross-Domain-Policies = "none"

# Website editor: never indexed, never cached, and only talks to this site (GitHub is reached through /api/gh).
[[headers]]
  for = "/studio/*"
  [headers.values]
    X-Robots-Tag = "noindex, nofollow"
    Cache-Control = "no-cache"
    Content-Security-Policy = "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob: https://avatars.githubusercontent.com; font-src 'self' data:; connect-src 'self'; media-src 'self' blob:; frame-src 'self' blob:; worker-src 'self' blob:; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"

# Caching for images and documents (pages themselves are always re-checked)
[[headers]]
  for = "/*.jpg"
  [headers.values]
    Cache-Control = "public, max-age=2592000"
[[headers]]
  for = "/*.png"
  [headers.values]
    Cache-Control = "public, max-age=2592000"
[[headers]]
  for = "/*.pdf"
  [headers.values]
    Cache-Control = "public, max-age=86400"

"""


def build_showcase():
    c = Ctx("show")
    views = ""
    for key in ["home", "services", "about", "contact", "privacy", "terms"]:
        views += '<div class="view" id="v-%s">%s</div>\n' % (key, fill(BUILDERS[key](c)))
    page = """<title>Finlume Website</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>%s</style>
<script>document.documentElement.setAttribute('data-mode','show');document.documentElement.classList.add('js');</script>
<div class="show-bar">Website preview, use the menu to move between pages. Live site: one file per page on Netlify.</div>
%s
<main id="main">%s</main>
%s
<script>%s</script>
""" % (CSS, header(c, "home"), views, fill(footer(c)), JS)
    p = os.path.join(HERE, "showcase.html")
    with open(p, "w", encoding="utf-8") as f:
        f.write(page)
    return p


if __name__ == "__main__":
    print(build_site())
    print(build_showcase())
