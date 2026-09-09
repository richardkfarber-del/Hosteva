"""US-015 — Checklist Available → Sign Up CTA (Curated Covered).

Guards Wasp copy bank + return-intent wiring. Does not change Curated allowlist.
"""
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

REPO_ROOT = Path(__file__).resolve().parents[1]
WIZARD = (REPO_ROOT / "app" / "templates" / "wizard.html").read_text()
REGISTER = (REPO_ROOT / "app" / "templates" / "register.html").read_text()


def test_wizard_covered_guest_cta_copy_and_register_next():
    """Guest Covered path: primary Sign Up CTA + helper + honesty; next → wizard checklist."""
    res = client.get("/wizard")
    assert res.status_code == 200
    body = res.text

    assert "Create a free account to see your checklist" in body
    assert "We'll save this address and open your free municipal checklist after you sign up. Takes a minute." in body
    assert "Research only — not a legal determination." in body
    assert "Already have an account?" in body
    assert "Open free checklist" not in body  # US-020: no redundant free-checklist CTA
    assert "checklistSignupCta" in body
    assert "buildRegisterUrlForChecklist" in body
    assert "intent=checklist" in body
    assert "/register?address=" in body
    assert "next=" in body
    # Must not send this CTA to pricing / Stripe
    assert "Create a free account to see your checklist" in body
    # Primary CTA builder must not target /pricing
    assert "buildRegisterUrlForChecklist" in body
    assert "/pricing" not in body.split("buildRegisterUrlForChecklist")[1].split("function buildLoginUrlForChecklist")[0]


def test_wizard_under_review_has_no_checklist_cta():
    """Under Review: Wasp title/body; no Checklist Available / free-checklist promise CTA."""
    body = WIZARD
    assert "function renderUnderReviewBanner" in body
    ur = body.split("function renderUnderReviewBanner")[1].split("async function runAudit")[0]
    assert "Under Review" in ur
    assert "no checklist to open" in ur
    assert "Research only — not a legal determination." in ur
    assert "Try another Florida address" in ur
    # Negative: no free-checklist / Checklist Available CTA on Under Review path
    assert "Create a free account to see your checklist" not in ur
    assert "Get your free checklist" not in ur
    assert "Open free checklist" not in ur
    assert "Checklist Available" not in ur
    assert "checklistSignupPrimaryBtn" not in ur


def test_register_honors_next_return_intent():
    """Post-signup uses relative next (wizard checklist) when present."""
    res = client.get("/register?address=10703%20Oak%20Drive%2C%20Hudson%2C%20FL&next=%2Fwizard%3Faddress%3D10703%26intent%3Dchecklist")
    assert res.status_code == 200
    body = res.text
    assert "urlParams.get('next')" in body or 'urlParams.get("next")' in body
    assert "nextParam.startsWith('/')" in body or 'nextParam.startsWith("/")' in body
    # Safe relative-only redirect (no open redirect)
    assert "startsWith('//')" in body or 'startsWith("//")' in body


def test_us015_does_not_touch_curated_allowlist():
    """Out of scope: CTA is template/auth next only — no Curated allowlist wiring."""
    curated = REPO_ROOT / "app" / "services" / "curated_coverage.py"
    assert curated.is_file()
    assert "curated_coverage" not in WIZARD
    assert "OPTION_B" not in WIZARD
    assert "hernando" not in WIZARD.lower()
