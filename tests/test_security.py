import re
from pathlib import Path

import pytest

import app as portfolio
from tests.conftest import https_client

PAGES = ["/", "/about", "/education", "/experience", "/projects", "/contact"]
HAS_RESUME = any((Path(portfolio.ROOT) / "static" / "resume").glob("*.pdf"))


def csp_of(resp):
    return dict(
        (part.split(" ", 1)[0], part.split(" ", 1)[1] if " " in part else "")
        for part in (p.strip() for p in resp.headers["Content-Security-Policy"].split(";"))
        if part
    )


# ── Pages and routes ─────────────────────────────────────────────────────────

@pytest.mark.parametrize("path", PAGES)
def test_pages_load(client, path):
    assert client.get(path).status_code == 200


def test_unknown_page_is_404(client):
    r = client.get("/does-not-exist")
    assert r.status_code == 404
    assert "404" in r.get_data(as_text=True)


def test_debug_endpoint_removed(client):
    assert client.get("/api/debug").status_code == 404


@pytest.mark.skipif(not HAS_RESUME, reason="no PDF in static/resume/")
def test_resume_is_pdf(client):
    r = client.get("/resume")
    assert r.status_code == 200
    assert r.mimetype == "application/pdf"


def test_no_open_redirect(client):
    # Send the raw path; the test client would otherwise read "//host" as a hostname.
    r = client.get("/", environ_overrides={"PATH_INFO": "//evil.example.com"})
    assert r.status_code == 404
    assert "Location" not in r.headers


def test_security_txt(client):
    r = client.get("/.well-known/security.txt")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "Contact: mailto:" in body and "Expires: " in body


def test_theme_assets_are_served(client):
    html = client.get("/").get_data(as_text=True)
    for path in (r"/static/css/site\.css", r"/theme-static/theme\.css"):
        css = re.search(rf'href="({path}\?v=\d+)"', html).group(1)
        r = client.get(css)
        assert r.status_code == 200 and r.mimetype == "text/css"
        assert "immutable" in r.headers["Cache-Control"]
    script = re.search(r'src="(/theme-static/theme\.js\?v=\d+)"', html)
    if script:
        assert client.get(script.group(1)).status_code == 200


# ── Security headers (OWASP Secure Headers Project) ──────────────────────────

@pytest.mark.parametrize("path", PAGES)
def test_security_headers(client, path):
    h = client.get(path).headers
    assert h["X-Content-Type-Options"] == "nosniff"
    assert h["X-Frame-Options"] == "DENY"
    assert h["X-XSS-Protection"] == "0"
    assert "max-age=31536000" in h["Strict-Transport-Security"]
    assert h["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert h["Cross-Origin-Opener-Policy"] == "same-origin"
    assert h["Cross-Origin-Resource-Policy"] == "same-origin"
    assert "camera=()" in h["Permissions-Policy"]


@pytest.mark.parametrize("path", PAGES)
def test_csp_is_strict(client, path):
    csp = csp_of(client.get(path))
    assert "'unsafe-inline'" not in csp["script-src"]
    assert "'unsafe-eval'" not in csp["script-src"]
    assert "http:" not in csp["script-src"] and "https:" not in csp["script-src"].replace("'self'", "")
    assert csp["frame-ancestors"] == "'none'"
    assert csp["object-src"] == "'none'"
    assert csp["base-uri"] == "'self'"
    assert csp["form-action"] == "'self'"


@pytest.mark.parametrize("path", PAGES)
def test_every_inline_script_carries_the_nonce(client, path):
    r = client.get(path)
    nonce = re.search(r"'nonce-([^']+)'", r.headers["Content-Security-Policy"]).group(1)
    html = r.get_data(as_text=True)
    for tag in re.findall(r"<script\b[^>]*>", html):
        if "src=" in tag:
            assert re.search(r'src="/(static|theme-static)/', tag), f"external script: {tag}"
        else:
            assert f'nonce="{nonce}"' in tag, f"inline script without nonce: {tag}"


def test_nonce_changes_per_request(client):
    a = client.get("/").headers["Content-Security-Policy"]
    b = client.get("/").headers["Content-Security-Policy"]
    assert re.search(r"nonce-[^']+", a).group() != re.search(r"nonce-[^']+", b).group()


@pytest.mark.parametrize("path", PAGES)
def test_no_inline_event_handlers(client, path):
    html = client.get(path).get_data(as_text=True)
    assert not re.search(r"<[^>]+\son[a-z]+\s*=", html)


@pytest.mark.parametrize("path", PAGES)
def test_new_tab_links_are_isolated(client, path):
    html = client.get(path).get_data(as_text=True)
    for tag in re.findall(r"<a\b[^>]*target=\"_blank\"[^>]*>", html):
        assert "noopener" in tag, tag


@pytest.mark.parametrize("path", PAGES)
def test_no_external_cdn_scripts_or_styles(client, path):
    html = client.get(path).get_data(as_text=True)
    for href in re.findall(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"', html):
        assert href.startswith(("/", "https://fonts.googleapis.com/")), href


def test_session_cookie_flags(client):
    client.get("/contact")
    cookie = client.get_cookie("__Host-session")
    assert cookie is not None
    assert cookie.secure and cookie.http_only
    assert cookie.same_site == "Strict"


# ── Contact form ─────────────────────────────────────────────────────────────

def test_contact_rejects_missing_csrf(client, monkeypatch):
    sent = []
    monkeypatch.setattr(portfolio.mail, "send", lambda m: sent.append(m))
    r = client.post("/contact", data={"name": "A", "email": "a@example.com", "message": "hello there friend"})
    assert r.status_code == 302
    assert not sent


def test_contact_strips_header_injection(app, monkeypatch):
    app.config["WTF_CSRF_ENABLED"] = False
    app.config.update(MAIL_USERNAME="me@example.com", MAIL_PASSWORD="x")
    sent = []
    monkeypatch.setattr(portfolio.mail, "send", lambda m: sent.append(m))
    https_client(app).post("/contact", data={
        "name": "Eve\r\nBcc: victim@example.com",
        "email": "eve@example.com",
        "message": "this is a long enough message",
        "type": "not-a-real-type",
    })
    assert len(sent) == 1
    assert "\n" not in sent[0].subject and "\r" not in sent[0].subject
    assert "Other enquiry" in sent[0].subject


def test_contact_offline_points_to_email(app):
    app.config["WTF_CSRF_ENABLED"] = False
    r = https_client(app).post("/contact", data={
        "name": "A", "email": "a@example.com", "message": "hello there friend"}, follow_redirects=True)
    assert "alex@example.com" in r.get_data(as_text=True)


def test_contact_rate_limit(app):
    app.config["WTF_CSRF_ENABLED"] = False
    c = https_client(app)
    data = {"name": "A", "email": "a@example.com", "message": "hello there friend"}
    for _ in range(5):
        c.post("/contact", data=data)
    r = c.post("/contact", data=data, follow_redirects=True)
    assert "Too many messages" in r.get_data(as_text=True)


def test_request_size_limit(app):
    app.config["WTF_CSRF_ENABLED"] = False
    r = https_client(app).post("/contact", data={"message": "x" * (64 * 1024)})
    assert r.status_code == 413


# ── Chat API ─────────────────────────────────────────────────────────────────

def test_chat_disabled_is_404():
    flask_app = portfolio.create_app(theme="terminal", overrides={"CHAT": {"enabled": False}})
    flask_app.config["WTF_CSRF_ENABLED"] = False
    c = https_client(flask_app)
    assert c.post("/api/chat", json={"message": "hi"}).status_code == 404
    assert 'id="chatForm"' not in c.get("/").get_data(as_text=True)


def test_chat_widget_shown_when_enabled(client):
    assert 'id="chatForm"' in client.get("/").get_data(as_text=True)


def test_chat_requires_csrf(client):
    assert client.post("/api/chat", json={"message": "hi"}).status_code == 400


def test_chat_requires_json(app):
    app.config["WTF_CSRF_ENABLED"] = False
    assert https_client(app).post("/api/chat", data="message=hi").status_code == 415


def test_chat_rejects_bad_payloads(app):
    app.config["WTF_CSRF_ENABLED"] = False
    c = https_client(app)
    for body in ({}, {"message": ""}, {"message": 123}, ["x"]):
        assert c.post("/api/chat", json=body).status_code == 400


def test_chat_hides_internal_errors(app):
    app.config["WTF_CSRF_ENABLED"] = False
    text = https_client(app).post("/api/chat", json={"message": "hi"}).get_data(as_text=True)
    assert "GROQ" not in text and "Traceback" not in text and "Error" not in text


def test_chat_rate_limit(app):
    app.config["WTF_CSRF_ENABLED"] = False
    c = https_client(app)
    codes = [c.post("/api/chat", json={"message": "hi"}).status_code for _ in range(13)]
    assert codes[-1] == 429


def test_chat_responses_not_cached(app):
    app.config["WTF_CSRF_ENABLED"] = False
    assert https_client(app).post("/api/chat", json={"message": "hi"}).headers["Cache-Control"] == "no-store"


# ── Helpers ──────────────────────────────────────────────────────────────────

def test_sanitize_text():
    assert portfolio.sanitize_text("<b>hi</b>", 100) == "&lt;b&gt;hi&lt;/b&gt;"
    assert portfolio.sanitize_text("a\r\nb", 100, single_line=True) == "a b"
    assert portfolio.sanitize_text("a\x00b\x07c", 100) == "abc"
    assert len(portfolio.sanitize_text("x" * 500, 100)) == 100


def test_rich_text_escapes_html():
    out = str(portfolio.rich("<script>x</script> **bold** and *accent*"))
    assert "<script>" not in out
    assert "<strong>bold</strong>" in out and "<em>accent</em>" in out
    assert portfolio.plain("Get in *touch*") == "Get in touch"


# ── Chat provider handling (provider mocked) ─────────────────────────────────

class _Resp:
    def __init__(self, body):
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _http_error(code, body):
    import io
    import urllib.error
    return urllib.error.HTTPError("https://api.example.com", code, "err", {}, io.BytesIO(body))


def test_chat_success_and_key_is_cleaned(app, monkeypatch):
    import json
    import urllib.request
    app.config["WTF_CSRF_ENABLED"] = False
    monkeypatch.setenv("GROQ_API_KEY", '  "gsk_test_key"\n')
    seen = {}

    def fake_urlopen(req, timeout=0):
        seen["auth"] = req.get_header("Authorization")
        return _Resp(json.dumps({"choices": [{"message": {"content": "He works in DFIR."}}]}).encode())

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    r = https_client(app).post("/api/chat", json={"message": "hi"})
    assert r.status_code == 200 and r.get_json()["reply"] == "He works in DFIR."
    assert seen["auth"] == "Bearer gsk_test_key"


def test_chat_falls_back_to_backup_model(app, monkeypatch):
    import json
    import urllib.request
    app.config["WTF_CSRF_ENABLED"] = False
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_key")
    models = []

    def fake_urlopen(req, timeout=0):
        models.append(json.loads(req.data)["model"])
        if len(models) == 1:
            raise _http_error(400, b'{"error":{"code":"model_decommissioned","message":"gone"}}')
        return _Resp(json.dumps({"choices": [{"message": {"content": "ok"}}]}).encode())

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    r = https_client(app).post("/api/chat", json={"message": "hi"})
    assert r.status_code == 200
    assert models == app.config["PORTFOLIO"]["CHAT"]["models"][:2]


def test_chat_bad_key_does_not_retry_or_leak(app, monkeypatch, caplog):
    import urllib.request
    app.config["WTF_CSRF_ENABLED"] = False
    monkeypatch.setenv("GROQ_API_KEY", "gsk_secret_value")
    calls = []

    def fake_urlopen(req, timeout=0):
        calls.append(1)
        raise _http_error(401, b'{"error":{"code":"invalid_api_key","message":"Invalid API Key"}}')

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    r = https_client(app).post("/api/chat", json={"message": "hi"})
    assert r.status_code == 502 and len(calls) == 1
    assert "invalid_api_key" in caplog.text
    assert "gsk_secret_value" not in caplog.text and "gsk_secret_value" not in r.get_data(as_text=True)


def test_chat_all_models_busy(app, monkeypatch):
    import urllib.request
    app.config["WTF_CSRF_ENABLED"] = False
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_key")

    def fake_urlopen(req, timeout=0):
        raise _http_error(429, b'{"error":{"code":"rate_limit_exceeded","message":"slow down"}}')

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    r = https_client(app).post("/api/chat", json={"message": "hi"})
    assert r.status_code == 429 and "try again in a minute" in r.get_json()["reply"]


def test_assistant_facts_come_from_config(app):
    with app.test_request_context("/api/chat"):
        text = portfolio.assistant_instructions()
    c = app.config["PORTFOLIO"]
    for job in c["EXPERIENCES"]:
        assert job["company"] in text and job["period"] in text
    for p in c["PROJECTS"]:
        assert "[" + p["title"] + "]" in text
    for cert in c["CERTIFICATIONS"]:
        assert cert["name"] in text
    assert c["PERSONAL"]["full_name"] in text
    assert "Never move a technology" in text


def test_reply_cleanup():
    raw = "**Tool**—a fine‑tuning platform.\n- built with Flask"
    assert portfolio.clean_reply(raw) == "Tool, a fine-tuning platform.\nbuilt with Flask"
