# -*- coding: utf-8 -*-
"""Website copy for Finlume.

All editable text lives in the content/*.json files. Those files are what the
Website editor (Decap CMS at /studio/) changes. This module loads them and
exposes the same names build.py has always used.
"""
import json, os, re

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content")


def _load(name):
    with open(os.path.join(_DIR, name + ".json"), encoding="utf-8") as f:
        return json.load(f)


def _s(v):
    return ("" if v is None else str(v)).strip()


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "service"


TEXT = {k: _load(k) for k in ("settings", "home", "services", "about", "contact")}
_S, _H, _V, _A = TEXT["settings"], TEXT["home"], TEXT["services"], TEXT["about"]

PHONE_DISPLAY = _s(_S.get("phone_display"))
PHONE_TEL = _s(_S.get("phone_tel")) or "+" + re.sub(r"\D", "", PHONE_DISPLAY)
WA_NUMBER = re.sub(r"\D", "", _s(_S.get("whatsapp_number")))
WA_TEXT = _s(_S.get("whatsapp_text"))
EMAIL = _s(_S.get("email"))
HOURS = _s(_S.get("hours"))
AREA = _s(_S.get("area"))
REG_NO = _s(_S.get("reg_no"))
PHYSICAL_ADDRESS = _s(_S.get("address"))
DOMAIN = "https://www.finlume.co.za"
FORM_TO = "info@finlume.co.za"

_seen = set()
SERVICES = []
for s in _V.get("services") or []:
    sid = _slug(_s(s.get("id")) or _s(s.get("title")))
    while sid in _seen:
        sid += "-2"
    _seen.add(sid)
    SERVICES.append(dict(id=sid, icon=_s(s.get("icon")) or "ledger", title=_s(s.get("title")), short=_s(s.get("short")),
                         long=_s(s.get("long")), items=[_s(x) for x in (s.get("items") or []) if _s(x)]))


def _rows(lst, *keys):
    return [tuple(_s(r.get(k)) for k in keys) for r in (lst or [])]


WHY = _rows(_H.get("why"), "icon", "title", "text")
COMPARE = _rows(_H.get("compare"), "item", "inhouse", "finlume")
DEADLINES = _rows(_H.get("deadlines"), "when", "often", "form", "what")
STEPS = _rows(_H.get("steps"), "title", "text")
SERVE = _rows(_H.get("serve"), "icon", "title", "text")
FAQ = _rows(_H.get("faq"), "question", "answer")
VALUES = _rows(_A.get("values"), "icon", "title", "text")
COMMITMENTS = _rows(_A.get("commitments"), "icon", "title", "text")
ENGAGEMENT = [(_s(e.get("title")), _s(e.get("text")), [_s(x) for x in (e.get("items") or []) if _s(x)], _s(e.get("best")))
              for e in (_V.get("engagement") or [])]
