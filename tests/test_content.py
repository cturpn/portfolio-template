"""config.py handling: defaults, validation and the theme switch."""
import re

import pytest

import app as portfolio
from content import ConfigError
from tests.conftest import https_client


def test_theme_env_override(monkeypatch):
    monkeypatch.setenv("PORTFOLIO_THEME", "editorial")
    flask_app = portfolio.create_app()
    assert flask_app.config["PORTFOLIO"]["THEME"] == "editorial"
    assert "/theme-static/theme.css" in https_client(flask_app).get("/").get_data(as_text=True)


def test_themes_share_one_page_structure():
    """Themes only change styling: the markup is identical apart from the theme's own asset tags."""
    def body(theme):
        html = https_client(portfolio.create_app(theme=theme)).get("/about").get_data(as_text=True)
        html = re.sub(r'<script src="/theme-static/[^"]*"></script>', "", html)
        html = re.sub(r'(nonce|content|value)="[^"]*"', "", html)   # per-request tokens
        return re.sub(r"\?v=\d+", "", html)
    assert body("console") == body("editorial") == body("terminal")


def test_unknown_option_is_reported():
    with pytest.raises(ConfigError, match=r"OPTIONS: unknown setting 'matrix_rain'"):
        portfolio.create_app(overrides={"OPTIONS": {"matrix_rain": True}})


def test_option_type_is_checked():
    with pytest.raises(ConfigError, match=r"OPTIONS.cert_band: expected bool"):
        portfolio.create_app(overrides={"OPTIONS": {"cert_band": "yes"}})


def test_old_theme_options_block_is_a_clear_error(monkeypatch, tmp_path):
    (tmp_path / "legacy_config.py").write_text('PERSONAL = {"first_name": "Ada"}\nTHEME_OPTIONS = {}\n')
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setenv("PORTFOLIO_CONFIG", "legacy_config")
    with pytest.raises(ConfigError, match="THEME_OPTIONS was replaced by OPTIONS"):
        portfolio.create_app()


def test_unknown_theme_is_a_clear_error():
    with pytest.raises(ConfigError, match="Available themes"):
        portfolio.create_app(theme="does-not-exist")


def test_missing_required_field():
    with pytest.raises(ConfigError, match=r"PERSONAL: 'first_name' is required"):
        portfolio.create_app(overrides={"PERSONAL": {"first_name": ""}})


def test_wrong_type_is_reported():
    with pytest.raises(ConfigError, match=r"PERSONAL.available: expected bool"):
        portfolio.create_app(overrides={"PERSONAL": {"available": "false"}})


def test_unknown_featured_slug():
    with pytest.raises(ConfigError, match="no project with slug 'nope'"):
        portfolio.create_app(overrides={"HOME": {"featured": ["nope"]}})


def test_duplicate_project_slug():
    projects = [{"slug": "a", "title": "A"}, {"slug": "a", "title": "B"}]
    with pytest.raises(ConfigError, match="used twice"):
        portfolio.create_app(overrides={"PROJECTS": projects, "PROJECT_GROUPS": [], "HOME": {"featured": []}})


def test_nav_must_name_real_pages():
    with pytest.raises(ConfigError, match="NAV entry 'blog'"):
        portfolio.create_app(overrides={"NAV": [("home", "Home"), ("blog", "Blog")]})


def test_errors_are_collected_together():
    with pytest.raises(ConfigError) as exc:
        portfolio.create_app(overrides={"LINKS": [{"label": "X"}], "CHAT": {"enabled": "yes"}})
    msg = str(exc.value)
    assert "LINKS[0]: 'url' is required" in msg and "CHAT.enabled: expected bool" in msg


def test_booking_needs_a_url():
    with pytest.raises(ConfigError, match=r"CONTACT.booking: 'url' is required"):
        portfolio.create_app(overrides={"CONTACT": {"booking": {"label": "Book"}}})


def test_booking_link_on_contact_page():
    url = "https://cal.com/example/intro"
    flask_app = portfolio.create_app(theme="console", overrides={"CONTACT": {"booking": {"url": url}}})
    page = https_client(flask_app).get("/contact").get_data(as_text=True)
    tags = re.findall(r'<a [^>]*href="' + re.escape(url) + r'"[^>]*>', page)
    assert tags and all('target="_blank"' in t and 'rel="noopener noreferrer"' in t for t in tags)
    assert "booking-card" not in https_client(portfolio.create_app(theme="console")).get("/contact").get_data(as_text=True)


@pytest.mark.parametrize("theme", ["terminal", "editorial", "console"])
def test_hidden_nav_page_still_works(theme):
    flask_app = portfolio.create_app(theme=theme, overrides={"NAV": [("home", "Home"), ("contact", "Contact")]})
    c = https_client(flask_app)
    home = c.get("/").get_data(as_text=True)
    assert 'href="/education"' not in home.split("</header>")[0]
    assert c.get("/education").status_code == 200


@pytest.mark.parametrize("theme", ["terminal", "editorial", "console"])
def test_availability_text_follows_config(theme):
    for available in (True, False):
        flask_app = portfolio.create_app(theme=theme, overrides={"PERSONAL": {"available": available}})
        text = flask_app.config["PORTFOLIO"]["PERSONAL"]["available_text" if available else "unavailable_text"]
        assert text in https_client(flask_app).get("/").get_data(as_text=True)


@pytest.mark.parametrize("theme", ["terminal", "editorial", "console"])
def test_example_config_renders(theme, monkeypatch):
    monkeypatch.setenv("PORTFOLIO_CONFIG", "config_example")
    flask_app = portfolio.create_app(theme=theme)
    c = https_client(flask_app)
    for path in ("/", "/about", "/education", "/experience", "/projects", "/contact"):
        assert c.get(path).status_code == 200, path


@pytest.mark.parametrize("theme", ["terminal", "editorial", "console"])
def test_minimal_config_renders(theme, monkeypatch):
    """A brand-new user who fills in only their name still gets a working site."""
    monkeypatch.setenv("PORTFOLIO_CONFIG", "tests.minimal_config")
    flask_app = portfolio.create_app(theme=theme)
    c = https_client(flask_app)
    for path in ("/", "/about", "/education", "/experience", "/projects", "/contact"):
        assert c.get(path).status_code == 200, path
