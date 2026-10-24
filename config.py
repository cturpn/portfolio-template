"""
Site content and settings. Everything a visitor sees comes from here.
Fill in the empty values below; config_example.py shows every option filled in.

Text fields accept two small markers:
    **bold**     -> strong text
    *accent*     -> the theme's accent style (green in "console"/"terminal", italic serif in "editorial")

Image paths are relative to static/ (e.g. "images/project1.png") or full https:// URLs.
Secrets (SECRET_KEY, mail password, API keys) belong in .env, never here.
"""

# Which look to use: "console", "terminal" or "editorial". Override with PORTFOLIO_THEME=... for a quick preview.
# Themes only change colours, fonts and effects; every setting below works the same in all of them.
THEME = "console"

SITE = {
    "title": "",                          # defaults to your full name when left out
    "description": "",                    # meta description for search engines
    "lang": "en",
}

# ── Who you are ─────────────────────────────────────────────────────────────
PERSONAL = {
    "first_name": "",                     # required: the site refuses to start without it
    "last_name": "",
    "roles": [],                          # e.g. ["Security Engineer", "Penetration Tester"]
    "tagline": "",
    "location": "",
    "timezone": "",                       # e.g. "Europe/Zurich"
    "email": "",                          # contact fallback, security.txt and the chat assistant
    # "photo": "images/me.jpg",           # optional; shown in the hero and About card
    "available": True,
    "available_text": "",
    "unavailable_text": "",
}

# ── Links ───────────────────────────────────────────────────────────────────
# show_in: any of "hero", "footer", "contact", "about"
# icon:    github, linkedin, mail, message, globe, file (see templates/_macros.html)
# e.g. {"id": "github", "label": "GitHub", "display": "github.com/you",
#       "url": "https://github.com/you", "show_in": ["hero", "footer", "contact", "about"]}
LINKS = []

# Pages in the menu, in order. Remove a line to hide that page from the menu.
NAV = [
    ("home", "Home"),
    ("about", "About"),
    ("projects", "Work"),
    ("experience", "Experience"),   # also shows certifications & education
    ("contact", "Contact"),
    # ("education", "Education"),   # hidden from the menu but still online
]

# Page headers. "command" is the small "$ ..." line above the headline.
PAGES = {
    "about":      {"command": "cat about.md",
                   "headline": ""},
    "education":  {"command": "cat education.json",
                   "headline": ""},
    "experience": {"command": "cat experience.log",
                   "headline": ""},
    "projects":   {"command": "ls -la ./projects/",
                   "headline": "",
                   "lead": ""},
    "contact":    {"command": "nc -lvnp 443",
                   "headline": "",
                   "lead": ""},
}

# ── Home page ───────────────────────────────────────────────────────────────
HOME = {
    "headline": "",
    "intro": "",
    # e.g. {"value": 3, "label": "Certifications", "suffix": "+"}
    "stats": [],
    # icon: bug, search, network, code, chart, flame, shield, lock, terminal, layers, flask
    # "meta" (optional): short note in the card corner, e.g. "2–5 days · from CHF 2'400"
    # e.g. {"title": "Penetration Testing", "icon": "bug", "description": "...", "tags": ["Nmap", "Burp Suite"]}
    "skill_groups": [],
    # Optional: [{"quote": "...", "name": "Jane Doe", "role": "IT Lead, Example AG"}]
    "testimonials": [],
    # Project slugs (see PROJECTS), shown as cards on the home page.
    "featured": [],
    "cta": {
        "title": "",
        "text": "",
        "button": "",
    },
}

# ── About page ──────────────────────────────────────────────────────────────
ABOUT = {
    "quote": "",
    "paragraphs": [],
    # Tag cloud under the bio.
    "skills": [],
    # e.g. {"label": "Location", "value": "Zurich, Switzerland"}
    "facts": [],
    # Optional "How I work" cards: [{"title": ..., "text": ...}]
    "principles": [],
    # Optional toolkit cards. Empty = reuse HOME.skill_groups.
    "toolkit": [],
}

# ── Education & certifications ──────────────────────────────────────────────
# e.g. {"title": "B.Sc. Computer Science", "school": "...", "subtitle": "...", "period": "2014 — 2018",
#       "badge": "B.Sc.", "notes": ["..."], "link": {"label": "View modules", "url": "https://..."}}
EDUCATION = []

# icon: award, shield, terminal, search, code, cap
# "url" (optional): the credential's verification page; the badge links to it.
# e.g. {"name": "Certified Penetration Testing Specialist (CPTS)", "short": "HTB CPTS",
#       "issuer": "Hack The Box", "year": "2026", "icon": "terminal"}
CERTIFICATIONS = []

# ── Experience (newest first) ───────────────────────────────────────────────
# A period containing "Present" is marked as current automatically.
# e.g. {"role": "Security Engineer", "company": "...", "period": "2024 – Present",
#       "location": "Hybrid", "bullets": ["..."], "skills": ["..."]}
EXPERIENCES = []

# ── Projects ────────────────────────────────────────────────────────────────
# Groups become filter buttons on the projects page, e.g. {"id": "tooling", "label": "Tools"}.
# Projects without images can set "preview": ["$ command", "output line", ...] for a terminal-style card.
PROJECT_GROUPS = []

# e.g. {"slug": "my-tool", "title": "...", "category": "...", "group": "tooling", "icon": "code",
#       "summary": "...", "description": "...", "images": ["images/project1.png"], "tags": ["..."]}
PROJECTS = []

# ── Contact page ────────────────────────────────────────────────────────────
CONTACT = {
    "intro": "",
    "response_time": "",
    "inquiry_types": [
        ("project", "Project inquiry"),
        ("job", "Job opportunity"),
        ("collaboration", "Collaboration"),
        ("other", "Something else"),
    ],
    # "Book a call" card above the form, and the header/hero buttons point there.
    # Opens your booking page in a new tab; nothing from the provider loads on this site.
    # e.g. {"url": "https://cal.com/yourname/intro", "label": "Book a 15-min call", "text": "Prefer to talk? ..."}
    "booking": None,
}

# ── Layout options (the same for every theme) ───────────────────────────────
OPTIONS = {
    "logo": True,                     # owl mark + favicon; False = initials
    "brand_tagline": "",              # under your name in the nav
    "hero_prompt": "whoami",          # the small "$ whoami" line above the headline; "" hides it
    # Header button and main hero button. Empty = "Book a call" to CONTACT.booking if set, else the contact page.
    "nav_cta": {},                    # e.g. {"label": "Hire me", "url": "..."}
    "hero_primary": {},
    "hero_secondary": {"label": "See my work"},
    "cert_band": True,                # certifications under the hero instead of HOME.stats
    "services_eyebrow": "What I do",
    "services_title": "Where I can *help*.",
    "light_toggle": True,             # the terminal theme is dark-only and hides it regardless
    "footer_note": "no trackers · strict CSP",
    "legal": "",                      # e.g. "Impressum · UID CHE-123.456.789"
}

# ── Site assistant (optional) ───────────────────────────────────────────────
# Needs an OpenAI-compatible API key in .env (GROQ_API_KEY by default).
# The assistant's knowledge is built from this file, so keep it accurate.
CHAT = {
    "enabled": False,
    "suggestions": [],
    "extra_facts": [],
}
