"""
Example content showing every option. Copy it over config.py to start fresh:

    cp config_example.py config.py

or preview it without copying:

    PORTFOLIO_CONFIG=config_example flask --app wsgi run

Text fields accept **bold** and *accent* markers. Image paths are relative to
static/ or full https:// URLs. Secrets belong in .env, never here.
"""

THEME = "console"            # "console", "terminal" or "editorial": colours, fonts and effects only

SITE = {
    "title": "Alex Morgan",
    "description": "Alex Morgan: security engineer focused on application security and detection.",
    "lang": "en",
}

PERSONAL = {
    "first_name": "Alex",
    "last_name": "Morgan",
    "roles": ["Application Security Engineer", "Detection Engineer", "Security Researcher"],
    "tagline": "AppSec · Detection · Research",
    "location": "Berlin, Germany",
    "timezone": "CET (UTC+1)",
    "email": "alex@example.com",
    "available": True,
    "available_text": "Open to new roles and engagements",
    "unavailable_text": "Not taking new work right now",
    # "initials": "AM",                 # monogram when OPTIONS.logo is False; defaults to your initials
}

LINKS = [
    {"id": "email", "label": "Email", "display": "alex@example.com", "icon": "mail",
     "url": "mailto:alex@example.com", "show_in": ["hero", "footer", "contact", "about"]},
    {"id": "github", "label": "GitHub", "display": "github.com/example",
     "url": "https://github.com/example", "show_in": ["hero", "footer", "contact", "about"]},
    {"id": "linkedin", "label": "LinkedIn", "display": "Alex Morgan",
     "url": "https://www.linkedin.com/in/example", "show_in": ["hero", "footer", "contact", "about"]},
    {"id": "blog", "label": "Blog", "display": "example.com/blog", "icon": "globe",
     "url": "https://example.com/blog", "show_in": ["footer", "contact"]},
]

NAV = [
    ("home", "Home"), ("projects", "Work"), ("experience", "Experience"),
    ("about", "About"), ("education", "Education"), ("contact", "Contact"),
]

PAGES = {
    "about":      {"command": "cat about.md"},
    "education":  {"command": "cat education.json",
                   "headline": "Degree, *certifications* and labs."},
    "experience": {"command": "cat experience.log",
                   "headline": "From help desk to *AppSec*.",
                   "lead": "Six years in IT and security, most recently on product security teams."},
    "projects":   {"command": "ls -la ./projects/",
                   "headline": "Things I've built and systems I've *tested*.",
                   "lead": "Client names and technical details of assessments stay confidential. "
                           "What you see here is scope, method and outcome."},
    "contact":    {"command": "nc -lvnp 443",
                   "headline": "Let's talk about your *next* project.",
                   "lead": "Full-time roles, security assessments or detection engineering work."},
}

HOME = {
    "headline": "Breaking things *responsibly*.",
    "intro": "I'm Alex, an application security engineer. I test web apps and APIs the way attackers "
             "would, and write the **detections** that catch them when they try.",
    "stats": [
        {"value": 120, "suffix": "+", "label": "Findings reported in recent assessments"},
        {"value": 40, "label": "Detection rules in production"},
        {"value": 6, "label": "Years in IT and security"},
        {"value": 3, "label": "Published CVEs"},
    ],
    "skill_groups": [
        {"title": "Application security", "icon": "shield",
         "description": "Web and API testing against the OWASP Top 10, with fixes engineers can ship.",
         "tags": ["Burp Suite", "OWASP ASVS", "Semgrep", "CVSS"]},
        {"title": "Detection engineering", "icon": "chart",
         "description": "Turning attacker behaviour into alerts that are worth waking up for.",
         "tags": ["Sigma", "KQL", "Splunk", "ATT&CK"]},
        {"title": "Research & tooling", "icon": "code",
         "description": "Small tools that make testing faster and findings reproducible.",
         "tags": ["Python", "Go", "Docker", "GitHub Actions"]},
    ],
    "featured": ["api-assessment", "detection-pipeline"],
    "cta": {
        "title": "An app that needs testing, or detections to *build*?",
        "text": "",
        "button": "Start a conversation",
    },
}

ABOUT = {
    "headline": "An engineer who likes to know how things *fail*.",
    "quote": "",
    "paragraphs": [
        "I started on a help desk, moved into systems administration, and found my way into "
        "security by breaking the things I was supposed to look after.",
        "Today I split my time between **testing applications** and **building detections**. "
        "Each makes me better at the other.",
    ],
    "skills": [],
    "facts": [
        {"label": "Focus", "value": "AppSec, detection"},
        {"label": "Work style", "value": "Remote or hybrid"},
    ],
    "principles": [
        {"title": "Evidence over opinion", "text": "Every finding is reproducible and scored."},
        {"title": "Root causes, not symptoms", "text": "Twenty findings with one cause deserve one fix."},
        {"title": "Discretion by default", "text": "Client systems and findings stay confidential."},
    ],
    "toolkit": [],      # empty = reuse HOME.skill_groups
}

EDUCATION = [
    {
        "school": "Example University",
        "title": "B.Sc. Computer Science",
        "subtitle": "Security track",
        "period": "2014 — 2018",
        "badge": "B.Sc.",
        "notes": ["Thesis: fuzzing JSON parsers", "Captain of the university CTF team"],
        "link": None,
    },
]

CERTIFICATIONS = [
    {"name": "Offensive Security Web Expert (OSWE)", "short": "OSWE", "issuer": "OffSec", "year": "2024", "icon": "terminal"},
    {"name": "GIAC Certified Detection Analyst (GCDA)", "short": "GCDA", "issuer": "GIAC", "year": "2023", "icon": "search"},
]

EXPERIENCES = [
    {
        "role": "Application Security Engineer",
        "company": "Example Corp",
        "url": "https://example.com",
        "period": "2022 — Present",
        "location": "Remote",
        "bullets": [
            "Lead web and API assessments for product teams before each major release.",
            "Built the detection pipeline that ships Sigma rules to the SIEM through CI.",
        ],
        "skills": ["Burp Suite", "Sigma", "Python"],
    },
    {
        "role": "Systems Administrator",
        "company": "Example Hosting",
        "period": "2018 — 2022",
        "location": "Berlin",
        "bullets": ["Ran Linux fleets of 300+ hosts and the patching programme behind them."],
        "skills": ["Linux", "Ansible", "Bash"],
    },
]

PROJECT_GROUPS = [
    {"id": "assessment", "label": "Security assessments"},
    {"id": "build", "label": "Engineering"},
]

PROJECTS = [
    {
        "slug": "api-assessment",
        "title": "Fintech API Assessment",
        "category": "Security assessment · API",
        "group": "assessment",
        "summary": "Authorisation and business-logic testing of a payments API.",
        "description": "Two-week authorised assessment of a payments API against the OWASP API Security Top 10.",
        "role": "Lead tester",
        "scope": ["180 endpoints", "3 user roles", "OWASP API Top 10"],
        "highlights": [
            "Found a tenant-isolation flaw that exposed other customers' invoices.",
            "Grouped 31 findings into 6 root causes so the team fixed less, properly.",
        ],
        # Shown instead of screenshots for confidential work
        "severity": [
            {"level": "critical", "label": "Critical", "count": 2},
            {"level": "high", "label": "High", "count": 7},
            {"level": "medium", "label": "Medium", "count": 14},
            {"level": "low", "label": "Low", "count": 8},
        ],
        "metric": ["31", "findings, 6 root causes"],
        "tags": ["Burp Suite", "Postman", "CVSS v3.1"],
        "note": "Client anonymised",
    },
    {
        "slug": "detection-pipeline",
        "title": "Detection-as-Code Pipeline",
        "category": "Engineering · Detection",
        "group": "build",
        "summary": "Sigma rules tested in CI and deployed to the SIEM on merge.",
        "description": "A pipeline that lints, unit-tests and converts Sigma rules, then deploys them on merge.",
        "images": [
            "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&q=80",
        ],
        "highlights": ["Cut rule deployment from days to minutes.", "Every rule ships with a test case."],
        "tags": ["Sigma", "Python", "GitHub Actions"],
        "link": "https://github.com/example",
        "link_label": "View on GitHub",
    },
]

CONTACT = {
    "intro": "I usually reply within one working day.",
    "response_time": "",
    "inquiry_types": [
        ("project", "A project or role"),
        ("assessment", "A security assessment"),
        ("other", "Something else"),
    ],
}

OPTIONS = {
    "logo": False,                    # True = owl mark + favicon, False = initials
    "brand_tagline": "AppSec · Detection · Research",
    "hero_prompt": "whoami",          # "" hides the "$ whoami" line
    "nav_cta": {},                    # e.g. {"label": "Hire me", "url": "https://cal.com/..."}
    "hero_primary": {},
    "hero_secondary": {"label": "See my work"},
    "cert_band": True,                # certifications under the hero instead of HOME.stats
    "services_eyebrow": "What I do",
    "services_title": "Where I can *help*.",
    "light_toggle": True,
    "footer_note": "no trackers · strict CSP",
    "legal": "",
}

CHAT = {
    "enabled": False,
    # OpenAI-compatible endpoint; the key comes from the env var named here.
    "endpoint": "https://api.groq.com/openai/v1/chat/completions",
    "api_key_env": "GROQ_API_KEY",
    "models": ["openai/gpt-oss-120b", "llama-3.3-70b-versatile"],
    "greeting": "Hi, I can answer questions about Alex's work, skills and availability.",
    "suggestions": ["What does Alex work on?", "Tell me about the API assessment", "Is Alex available?"],
    "extra_facts": ["Alex speaks English and German."],
}
