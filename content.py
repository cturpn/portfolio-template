"""
Loads config.py, fills in defaults and checks it, so a typo in the content
fails at start-up with a clear message instead of as a broken page.

Set PORTFOLIO_CONFIG to load a different module (e.g. config_example).
"""

import copy
import importlib
import os

SECTIONS = (
    "THEME", "SITE", "PERSONAL", "LINKS", "NAV", "PAGES", "HOME", "ABOUT", "EDUCATION",
    "CERTIFICATIONS", "EXPERIENCES", "PROJECTS", "PROJECT_GROUPS", "CONTACT",
    "OPTIONS", "CHAT",
)

DEFAULT_NAV = [
    ("home", "Home"), ("about", "About"), ("education", "Education"),
    ("experience", "Experience"), ("projects", "Projects"), ("contact", "Contact"),
]

DEFAULT_PAGES = {
    "about":      {"command": "cat about.md",       "headline": "About *me*", "lead": ""},
    "education":  {"command": "cat education.json", "headline": "Education & *credentials*", "lead": ""},
    "experience": {"command": "cat experience.log", "headline": "Work *experience*", "lead": ""},
    "projects":   {"command": "ls -la ./projects/", "headline": "Selected *projects*", "lead": ""},
    "contact":    {"command": "nc -lvnp 443",       "headline": "Get in *touch*", "lead": ""},
}

# Layout switches. Every theme renders the same templates, so these apply to all of them.
DEFAULT_OPTIONS = {
    "logo": False,
    "brand_tagline": "",
    "hero_prompt": "whoami",
    "nav_cta": {},
    "hero_primary": {},
    "hero_secondary": {},
    "cert_band": True,
    "services_eyebrow": "What I do",
    "services_title": "Where I can *help*.",
    "light_toggle": True,
    "footer_note": "no trackers · strict CSP",
    "legal": "",
}

DEFAULT_INQUIRY_TYPES = [
    ("project", "A project or role"),
    ("collaboration", "Collaboration"),
    ("mentorship", "Mentorship"),
    ("other", "Something else"),
]


class ConfigError(Exception):
    """config.py is missing something or has a value of the wrong type."""


class _Checker:
    def __init__(self):
        self.errors = []

    def need(self, obj, key, kind, where):
        if not isinstance(obj, dict) or key not in obj or obj[key] in (None, ""):
            self.errors.append(f"{where}: '{key}' is required")
            return False
        return self.kind(obj[key], kind, f"{where}.{key}")

    def kind(self, value, kind, where):
        if not isinstance(value, kind):
            names = " or ".join(k.__name__ for k in (kind if isinstance(kind, tuple) else (kind,)))
            self.errors.append(f"{where}: expected {names}, got {type(value).__name__}")
            return False
        return True

    def items(self, value, where):
        """Yield (index, dict) for a list of dicts, reporting anything else."""
        if not self.kind(value, list, where):
            return
        for i, item in enumerate(value):
            if self.kind(item, dict, f"{where}[{i}]"):
                yield i, item


def load_content(overrides: dict | None = None) -> dict:
    module = importlib.import_module(os.getenv("PORTFOLIO_CONFIG", "config"))
    if hasattr(module, "THEME_OPTIONS"):
        raise ConfigError("config.py: THEME_OPTIONS was replaced by OPTIONS, one block shared by all themes. "
                          "Move the settings you use into OPTIONS (see config_example.py).")
    data = {name: copy.deepcopy(getattr(module, name)) for name in SECTIONS if hasattr(module, name)}
    for key, value in (overrides or {}).items():
        if isinstance(value, dict) and isinstance(data.get(key), dict):
            data[key] = {**data[key], **value}
        else:
            data[key] = value
    normalise(data)
    return data


def normalise(d: dict) -> None:
    c = _Checker()
    d.setdefault("THEME", "console")

    # ── Personal ──────────────────────────────────────────────────────────────
    p = d.setdefault("PERSONAL", {})
    c.need(p, "first_name", str, "PERSONAL")
    p.setdefault("last_name", "")
    p["full_name"] = f"{p.get('first_name', '')} {p['last_name']}".strip()
    p.setdefault("roles", [])
    c.kind(p["roles"], list, "PERSONAL.roles")
    p.setdefault("available", True)
    c.kind(p["available"], bool, "PERSONAL.available")
    p.setdefault("available_text", "Open to new opportunities")
    p.setdefault("unavailable_text", "Not available right now")
    p["status_text"] = p["available_text"] if p["available"] is True else p["unavailable_text"]
    p.setdefault("initials", "".join(w[0] for w in p["full_name"].split()[:2]).upper())
    for key in ("tagline", "location", "timezone", "email", "bio", "photo"):
        p.setdefault(key, "")

    # ── Site ──────────────────────────────────────────────────────────────────
    s = d.setdefault("SITE", {})
    s.setdefault("title", p["full_name"])
    s.setdefault("description", p.get("tagline", ""))
    s.setdefault("lang", "en")

    # ── Links ─────────────────────────────────────────────────────────────────
    links = d.setdefault("LINKS", [])
    for i, link in c.items(links, "LINKS"):
        where = f"LINKS[{i}]"
        c.need(link, "label", str, where)
        c.need(link, "url", str, where)
        link.setdefault("id", str(link.get("label", "")).lower())
        link.setdefault("icon", link["id"])
        link.setdefault("display", link.get("label", ""))
        link.setdefault("show_in", ["footer", "contact"])
        link["external"] = str(link.get("url", "")).startswith(("http://", "https://"))

    # ── Navigation & page headers ─────────────────────────────────────────────
    nav = d.setdefault("NAV", DEFAULT_NAV)
    d["NAV"] = [tuple(item) for item in nav]
    pages = d.setdefault("PAGES", {})
    for name, defaults in DEFAULT_PAGES.items():
        pages[name] = {**defaults, **pages.get(name, {})}

    # ── Projects ──────────────────────────────────────────────────────────────
    groups = d.setdefault("PROJECT_GROUPS", [])
    group_ids = set()
    for i, g in c.items(groups, "PROJECT_GROUPS"):
        if c.need(g, "id", str, f"PROJECT_GROUPS[{i}]"):
            group_ids.add(g["id"])
        g.setdefault("label", g.get("id", ""))
    slugs = set()
    projects = d.setdefault("PROJECTS", [])
    for i, pr in c.items(projects, "PROJECTS"):
        where = f"PROJECTS[{i}]"
        c.need(pr, "title", str, where)
        if c.need(pr, "slug", str, where):
            if pr["slug"] in slugs:
                c.errors.append(f"{where}: slug '{pr['slug']}' is used twice")
            slugs.add(pr["slug"])
        pr.setdefault("summary", pr.get("description", ""))
        pr.setdefault("description", pr["summary"])
        pr.setdefault("category", "Project")
        pr.setdefault("icon", "shield")
        for key in ("images", "tags", "highlights", "scope", "severity", "preview"):
            pr.setdefault(key, [])
            c.kind(pr[key], list, f"{where}.{key}")
        pr.setdefault("group", groups[0]["id"] if groups and isinstance(groups[0], dict) and "id" in groups[0] else "")
        if group_ids and pr["group"] not in group_ids:
            c.errors.append(f"{where}: group '{pr['group']}' is not in PROJECT_GROUPS ({', '.join(sorted(group_ids))})")
        pr.setdefault("link", None)
        pr.setdefault("link_label", "Read report")
        for key in ("role", "note", "metric"):
            pr.setdefault(key, None)

    # ── Home ──────────────────────────────────────────────────────────────────
    h = d.setdefault("HOME", {})
    h.setdefault("headline", p["full_name"])
    h.setdefault("intro", p.get("bio", ""))
    h.setdefault("stats", [])
    for i, st in c.items(h["stats"], "HOME.stats"):
        c.need(st, "value", int, f"HOME.stats[{i}]")
        c.need(st, "label", str, f"HOME.stats[{i}]")
        st.setdefault("suffix", "")
    h.setdefault("skill_groups", [])
    for i, sg in c.items(h["skill_groups"], "HOME.skill_groups"):
        c.need(sg, "title", str, f"HOME.skill_groups[{i}]")
        sg.setdefault("icon", "shield")
        sg.setdefault("description", "")
        sg.setdefault("tags", [])
        sg.setdefault("meta", "")
    h.setdefault("testimonials", [])
    for i, t in c.items(h["testimonials"], "HOME.testimonials"):
        c.need(t, "quote", str, f"HOME.testimonials[{i}]")
        c.need(t, "name", str, f"HOME.testimonials[{i}]")
        t.setdefault("role", "")
    h.setdefault("featured", [])
    for slug in h["featured"]:
        if slug not in slugs:
            c.errors.append(f"HOME.featured: no project with slug '{slug}'")
    h.setdefault("cta", {})
    h["cta"].setdefault("title", "Let's *talk*")
    h["cta"].setdefault("text", "")
    h["cta"].setdefault("button", "Get in touch")

    # ── About ─────────────────────────────────────────────────────────────────
    a = d.setdefault("ABOUT", {})
    a.setdefault("headline", d["PAGES"]["about"]["headline"])
    for key in ("paragraphs", "skills", "facts", "principles", "toolkit"):
        a.setdefault(key, [])
        c.kind(a[key], list, f"ABOUT.{key}")
    a.setdefault("quote", "")

    # ── Education, certifications, experience ─────────────────────────────────
    for i, e in c.items(d.setdefault("EDUCATION", []), "EDUCATION"):
        c.need(e, "title", str, f"EDUCATION[{i}]")
        for key in ("school", "subtitle", "period", "badge"):
            e.setdefault(key, "")
        e.setdefault("notes", [])
        e.setdefault("link", None)
    for i, cert in c.items(d.setdefault("CERTIFICATIONS", []), "CERTIFICATIONS"):
        c.need(cert, "name", str, f"CERTIFICATIONS[{i}]")
        cert.setdefault("short", cert.get("name", ""))
        cert.setdefault("issuer", "")
        cert.setdefault("year", "")
        cert.setdefault("icon", "award")
        cert.setdefault("url", None)
    for i, job in c.items(d.setdefault("EXPERIENCES", []), "EXPERIENCES"):
        c.need(job, "role", str, f"EXPERIENCES[{i}]")
        c.need(job, "company", str, f"EXPERIENCES[{i}]")
        job.setdefault("period", "")
        job.setdefault("location", "")
        job.setdefault("url", None)
        job.setdefault("bullets", [])
        job.setdefault("skills", [])
        job.setdefault("current", "present" in str(job["period"]).lower())

    # ── Contact ───────────────────────────────────────────────────────────────
    ct = d.setdefault("CONTACT", {})
    ct.setdefault("intro", "")
    ct.setdefault("response_time", "")
    ct["inquiry_types"] = [tuple(t) for t in ct.get("inquiry_types", DEFAULT_INQUIRY_TYPES)]
    if "other" not in {v for v, _ in ct["inquiry_types"]}:
        ct["inquiry_types"].append(("other", "Something else"))
    ct.setdefault("booking", None)
    if ct["booking"] is not None and c.kind(ct["booking"], dict, "CONTACT.booking"):
        c.need(ct["booking"], "url", str, "CONTACT.booking")
        ct["booking"].setdefault("label", "Book a 15-min call")
        ct["booking"].setdefault("text", "Prefer to talk? 15 minutes, no sales pitch.")

    # ── Layout options & chat ─────────────────────────────────────────────────
    o = d.setdefault("OPTIONS", {})
    if c.kind(o, dict, "OPTIONS"):
        for key in o.keys() - DEFAULT_OPTIONS.keys():
            c.errors.append(f"OPTIONS: unknown setting '{key}' (known: {', '.join(DEFAULT_OPTIONS)})")
        for key, default in DEFAULT_OPTIONS.items():
            o.setdefault(key, copy.deepcopy(default))
            c.kind(o[key], type(default), f"OPTIONS.{key}")
    chat = d.setdefault("CHAT", {})
    chat.setdefault("enabled", False)
    c.kind(chat["enabled"], bool, "CHAT.enabled")
    chat.setdefault("endpoint", "https://api.groq.com/openai/v1/chat/completions")
    chat.setdefault("models", ["openai/gpt-oss-120b", "llama-3.3-70b-versatile"])
    chat.setdefault("api_key_env", "GROQ_API_KEY")
    chat.setdefault("greeting", f"Hi, I can answer questions about {p.get('first_name', 'me')}'s work, skills and availability.")
    chat.setdefault("suggestions", [])
    chat.setdefault("extra_facts", [])

    if c.errors:
        raise ConfigError("config.py has problems:\n  - " + "\n  - ".join(c.errors))
