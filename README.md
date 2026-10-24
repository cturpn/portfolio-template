# Security Portfolio Template

A hardened Flask portfolio for security people. All the content lives in one file (`config.py`), and the look comes from a swappable theme.

| Theme | Look |
|---|---|
| `console` | Mono headings, one green accent, no third-party fonts (the default) |
| `terminal` | Neon green, mono everywhere, scanlines and matrix rain. Dark only |
| `editorial` | Calm and type-led, sans headings with a serif-italic accent |

All themes share one set of templates and one layout stylesheet, so every page and every setting works the same in each. A theme only changes colours, fonts and small effects. The pages are Home, About, Education, Experience, Projects and Contact, with an optional AI site assistant.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then set SECRET_KEY (command is in the file)
# fill in config.py (at least PERSONAL.first_name, or the app refuses to start) 
flask --app wsgi run
```

Open http://127.0.0.1:5000. The session cookie is `Secure`, which browsers allow on `localhost`.

## Make it yours

1. Edit **`config.py`**. Every section is commented. To start from scratch, look at `config_example.py`, which uses every option.
2. Put images in `static/images/` and refer to them as `"images/name.png"`, or use full `https://` URLs.
3. Put your CV in `static/resume/` as a PDF. `/resume` serves the first PDF it finds there.

Text fields accept two markers: `**bold**` and `*accent*`. The accent renders as green text in `terminal` and as serif italic in `editorial`.

If something in `config.py` is missing or has the wrong type, the app refuses to start and lists every problem, for example:

```
content.ConfigError: config.py has problems:
  - PERSONAL.available: expected bool, got str
  - HOME.featured: no project with slug 'website-monitr'
```

### Config reference

| Section | What it holds |
|---|---|
| `THEME` | `"console"`, `"terminal"` or `"editorial"` |
| `SITE` | Page title, meta description, language |
| `PERSONAL` | Name, roles, location, time zone, email, `available` (bool) and its two status texts |
| `LINKS` | One list of links. `show_in` decides where each appears: `hero`, `footer`, `contact` or `about` |
| `NAV` | Menu order and labels. Remove an entry to hide that page from the menu |
| `PAGES` | Per-page `headline`, `lead` and `command` (the small `$ ...` line above the headline) |
| `HOME` | Hero headline and intro, stats, skill groups, featured project slugs, closing call to action |
| `ABOUT` | Quote, paragraphs, skill tags, quick facts, optional principles and toolkit |
| `EDUCATION`, `CERTIFICATIONS`, `EXPERIENCES` | Lists, newest first. A period containing "Present" is marked as current |
| `PROJECTS`, `PROJECT_GROUPS` | Projects with images (or a `severity` breakdown for confidential work); groups become filter buttons |
| `CONTACT` | Intro text, response time, enquiry types for the form, and an optional `booking` link (`{"url": ...}`) for a "Book a call" card |
| `OPTIONS` | Layout switches shared by all themes: logo, nav tagline, hero prompt and buttons, certification band, services heading, light/dark toggle, footer note and legal line. Unknown keys are reported at startup |
| `CHAT` | Turns the site assistant on and sets its models. Its knowledge is built from this file |

## Switching themes

Set `THEME` in `config.py`, or preview another theme without editing it:

```bash
PORTFOLIO_THEME=editorial flask --app wsgi run
PORTFOLIO_CONFIG=config_example flask --app wsgi run    # preview the example content
```

## Adding a theme

A theme is a folder under `themes/` with a `theme.css`, and optionally a `theme.js`. Nothing else.

1. Copy a theme folder, e.g. `themes/editorial`, to `themes/mytheme`.
2. In `theme.css`, override the tokens defined at the top of `static/css/site.css`: colours (for `:root` and `:root[data-theme="light"]`), `--font-sans`, `--font-mono`, `--font-display` (headings), `--em-font` / `--em-style` (the `*accent*` text), and `--radius` / `--radius-lg`. Add small rules for anything else. Web fonts can come in via `@import` from Google Fonts.
3. `theme.js` is loaded after `static/js/core.js` when present (the terminal theme uses it for matrix rain). Keep it self-contained, respect `prefers-reduced-motion`, and don't load third-party scripts: the CSP blocks them.

Layout changes go in the shared `templates/` and `static/css/site.css`, so every theme gets them.

## Security

Enforced by the test suite, for every theme (the suite also checks that all themes render identical markup):

- Strict nonce-based CSP (no inline scripts, no CDNs), plus the OWASP secure headers
- CSRF tokens on the contact form and the chat API
- `__Host-` session cookie: Secure, HttpOnly, SameSite=Strict
- Contact form: input sanitising, mail-header-injection protection, rate limiting, 32 KB request limit
- Chat: JSON-only, rate limited, provider errors logged without the key and never shown to visitors
- `/.well-known/security.txt` generated from your email

Secrets (`SECRET_KEY`, mail credentials, API key) are read from `.env` only.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Deploying

Any host that runs `gunicorn wsgi:app` works (a `Procfile` is included). Set the variables from `.env.example` in the host's dashboard. Set `TRUST_PROXY=0` if the app is **not** behind a reverse proxy.

## Credits

- Idea, initial template & chatbot integration: Timothy Victor Osas ([Osvic1](https://github.com/Osvic1))
