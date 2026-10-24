# Security Portfolio Template

A hardened Flask portfolio for security people. All the content lives in one file (`config.py`), and the look comes from a swappable theme.

| Theme | Look |
|---|---|
| `console` | Mono headings, one green accent, no third-party fonts (the default) |
| `terminal` | Neon green, mono everywhere, scanlines and matrix rain. Dark only |
| `editorial` | Calm and type-led, sans headings with a serif-italic accent |


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

## Switching themes

Set `THEME` in `config.py`, or preview another theme without editing it:

```bash
PORTFOLIO_THEME=editorial flask --app wsgi run
PORTFOLIO_CONFIG=config_example flask --app wsgi run    # preview the example content
```

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

## AI Usage

AI was used to assist in formatting, documenting and writing sections of the template. 
All code has been reviewed by me. 
