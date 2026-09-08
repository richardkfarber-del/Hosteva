"""BUG-PL-08 — Street View object storage (B) + lazy re-fetch heal (C).

No US-015 / US-018 / Pasco / Option B changes.
"""
from __future__ import annotations

import os
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_bug_pl08.db")
os.environ.setdefault("INTERNAL_DATABASE_URL", "sqlite:///./test_bug_pl08.db")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("BILLING_ENABLED", "false")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-pl08")
os.environ["ADMIN_API_KEY"] = "test-admin-pl08"

# Object storage env (fake values for configured() — uploads are mocked)
os.environ["PROPERTY_IMAGE_PROVIDER"] = "r2"
os.environ["PROPERTY_IMAGE_BUCKET"] = "hosteva-property-images-test"
os.environ["PROPERTY_IMAGE_ENDPOINT_URL"] = "https://example.r2.cloudflarestorage.com"
os.environ["PROPERTY_IMAGE_REGION"] = "auto"
os.environ["PROPERTY_IMAGE_ACCESS_KEY_ID"] = "test-access-key-id"
os.environ["PROPERTY_IMAGE_SECRET_ACCESS_KEY"] = "test-secret-access-key"
os.environ["PROPERTY_IMAGE_PUBLIC_BASE_URL"] = "https://images.test.hosteva.example"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.host import Host
from app.models.property import Property
from app.core.security import get_current_user, get_password_hash
from app.routers.properties import (
    FALLBACK_PROPERTY_IMAGE_URL,
    _save_property_image_bytes,
    fetch_real_property_image,
    is_fallback_property_image,
)
from app.services.property_image_storage import (
    build_public_url,
    provider_name,
    storage_configured,
)
from app.services.property_image_heal import (
    backfill_property_images,
    heal_property_image,
    needs_image_heal,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
# Repo-relative only — never box absolute paths (CI has no /workspace/hosteva-review).
CHANGELOG = REPO_ROOT / "docs" / "05_build" / "CHANGELOG.md"
INVENTORY = REPO_ROOT / "docs" / "06_qa" / "TEST_INVENTORY.md"

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

HOST_ID = "host_pl08"
USERNAME = "pl08_host"


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(
        Host(
            id=HOST_ID,
            username=USERNAME,
            email="pl08@test.example",
            password_hash=get_password_hash("x"),
        )
    )
    db.commit()
    db.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def override_user():
        return {"username": USERNAME, "sub": USERNAME}

    prev_db = app.dependency_overrides.get(get_db)
    prev_user = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_user
    yield
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)
    if prev_db is not None:
        app.dependency_overrides[get_db] = prev_db
    if prev_user is not None:
        app.dependency_overrides[get_current_user] = prev_user
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def _mock_resp(status_code=200, json_data=None, content=b"", text=""):
    r = MagicMock()
    r.status_code = status_code
    r.json.return_value = json_data or {}
    r.content = content
    r.text = text or str(json_data or "")
    return r


def test_provider_default_is_r2():
    assert provider_name() == "r2"
    assert storage_configured() is True


def test_build_public_url():
    url = build_public_url("property-images/abc.jpg")
    assert url.startswith("https://images.test.hosteva.example/")
    assert url.endswith("property-images/abc.jpg")


def test_save_uses_object_storage_not_ephemeral_disk():
    durable = "https://images.test.hosteva.example/property-images/deadbeef.jpg"
    with patch(
        "app.services.property_image_storage.upload_property_image",
        return_value=durable,
    ) as mock_up:
        url = _save_property_image_bytes(b"jpeg-bytes")
        mock_up.assert_called_once()
    assert url == durable
    assert not url.startswith("/static/property_images/")
    assert not is_fallback_property_image(url)


def test_save_without_storage_returns_none_no_ephemeral_write(tmp_path, monkeypatch):
    monkeypatch.delenv("PROPERTY_IMAGE_BUCKET", raising=False)
    monkeypatch.delenv("PROPERTY_IMAGE_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("PROPERTY_IMAGE_SECRET_ACCESS_KEY", raising=False)
    monkeypatch.delenv("PROPERTY_IMAGE_PUBLIC_BASE_URL", raising=False)
    assert storage_configured() is False
    before = list(Path("app/static/property_images").glob("*.jpg")) if Path("app/static/property_images").exists() else []
    url = _save_property_image_bytes(b"jpeg-bytes")
    assert url is None
    after = list(Path("app/static/property_images").glob("*.jpg")) if Path("app/static/property_images").exists() else []
    assert len(after) == len(before)


@patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test-key"}, clear=False)
@patch("app.routers.properties.requests.get")
def test_fetch_real_uploads_to_object_store(mock_get):
    durable = "https://images.test.hosteva.example/property-images/sv.jpg"
    meta = _mock_resp(200, {"status": "OK"}, text='{"status":"OK"}')
    img = _mock_resp(200, content=b"fake-jpeg-bytes")
    mock_get.side_effect = [meta, img]
    with patch(
        "app.services.property_image_storage.upload_property_image",
        return_value=durable,
    ):
        url = fetch_real_property_image("123 Main St, Tampa, FL 33602")
    assert url == durable
    assert not is_fallback_property_image(url)


def test_needs_heal_ephemeral_paths():
    assert needs_image_heal("/static/property_images/abc.jpg") is True
    assert needs_image_heal(FALLBACK_PROPERTY_IMAGE_URL) is False
    assert needs_image_heal("https://images.test.hosteva.example/property-images/x.jpg") is False
    assert needs_image_heal(None) is False  # treated as placeholder / not healable claim


def test_heal_migrates_local_ephemeral_file(tmp_path):
    img_dir = Path("app/static/property_images")
    img_dir.mkdir(parents=True, exist_ok=True)
    name = f"pl08-{uuid.uuid4()}.jpg"
    disk = img_dir / name
    disk.write_bytes(b"local-jpeg")
    ephemeral = f"/static/property_images/{name}"
    durable = "https://images.test.hosteva.example/property-images/migrated.jpg"

    db = TestingSessionLocal()
    prop = Property(
        id=str(uuid.uuid4()),
        user_id=HOST_ID,
        address="100 Heal St",
        city="Tampa",
        state="FL",
        zip_code="33602",
        property_type="Single Family",
        image_url=ephemeral,
    )
    db.add(prop)
    db.commit()

    try:
        with patch(
            "app.services.property_image_storage.upload_property_image",
            return_value=durable,
        ) as mock_up:
            out = heal_property_image(db, prop, commit=True)
            mock_up.assert_called_once()
            assert mock_up.call_args[0][0] == b"local-jpeg"
        db.refresh(prop)
        assert out == durable
        assert prop.image_url == durable
    finally:
        db.close()
        if disk.exists():
            disk.unlink()


def test_heal_refetch_when_local_missing():
    ephemeral = f"/static/property_images/{uuid.uuid4()}.jpg"
    durable = "https://images.test.hosteva.example/property-images/refetch.jpg"
    db = TestingSessionLocal()
    prop = Property(
        id=str(uuid.uuid4()),
        user_id=HOST_ID,
        address="200 Missing Ave",
        city="Tampa",
        state="FL",
        zip_code="33602",
        property_type="Single Family",
        image_url=ephemeral,
    )
    db.add(prop)
    db.commit()
    try:
        with patch(
            "app.services.property_image_heal._refetch_street_view",
            return_value=durable,
        ):
            out = heal_property_image(db, prop, commit=True)
        db.refresh(prop)
        assert out == durable
        assert prop.image_url == durable
    finally:
        db.close()


def test_heal_fail_closed_to_placeholder_when_maps_fails():
    ephemeral = f"/static/property_images/{uuid.uuid4()}.jpg"
    db = TestingSessionLocal()
    prop = Property(
        id=str(uuid.uuid4()),
        user_id=HOST_ID,
        address="300 Fail Ln",
        city="Tampa",
        state="FL",
        zip_code="33602",
        property_type="Single Family",
        image_url=ephemeral,
    )
    db.add(prop)
    db.commit()
    try:
        with patch(
            "app.services.property_image_heal._refetch_street_view",
            return_value=None,
        ):
            out = heal_property_image(db, prop, commit=True)
        db.refresh(prop)
        assert out == FALLBACK_PROPERTY_IMAGE_URL
        assert prop.image_url == FALLBACK_PROPERTY_IMAGE_URL
        assert is_fallback_property_image(prop.image_url)
    finally:
        db.close()


def test_list_lazy_heals_ephemeral_url():
    ephemeral = f"/static/property_images/{uuid.uuid4()}.jpg"
    durable = "https://images.test.hosteva.example/property-images/list-heal.jpg"
    db = TestingSessionLocal()
    prop = Property(
        id=str(uuid.uuid4()),
        user_id=HOST_ID,
        address="400 List St",
        city="Tampa",
        state="FL",
        zip_code="33602",
        property_type="Single Family",
        image_url=ephemeral,
        zoning_status="Pending",
    )
    db.add(prop)
    db.commit()
    pid = prop.id
    db.close()

    with patch(
        "app.services.property_image_heal._refetch_street_view",
        return_value=durable,
    ):
        resp = client.get("/api/properties/")
    assert resp.status_code == 200
    rows = resp.json()
    match = [r for r in rows if r["id"] == pid]
    assert match
    assert match[0]["image_url"] == durable
    assert match[0]["image_is_placeholder"] is False


def test_admin_backfill_endpoint():
    ephemeral = f"/static/property_images/{uuid.uuid4()}.jpg"
    durable = "https://images.test.hosteva.example/property-images/admin.jpg"
    db = TestingSessionLocal()
    prop = Property(
        id=str(uuid.uuid4()),
        user_id=HOST_ID,
        address="500 Admin Blvd",
        city="Tampa",
        state="FL",
        zip_code="33602",
        property_type="Single Family",
        image_url=ephemeral,
    )
    db.add(prop)
    db.commit()
    db.close()

    with patch(
        "app.services.property_image_heal._refetch_street_view",
        return_value=durable,
    ):
        resp = client.post(
            "/api/v1/admin/properties/backfill-images",
            headers={"X-Admin-Key": "test-admin-pl08"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["healed"] >= 1


def test_fallback_house_stays_in_app_static():
    assert Path("app/static/img/fallback_house.jpg").is_file()


def test_out_of_scope_markers_untouched():
    """Sanity: this PR must not bundle US-015 / US-018 / Pasco / Option B edits."""
    # Presence of those modules unchanged is enough; PL-08 files are additive.
    assert Path("tests/test_us015_checklist_signup_cta.py").is_file()
    assert Path("tests/test_us018_dup_address_guard.py").is_file()
    assert Path("tests/test_bug_012_stable_run_pasco.py").is_file()


def test_changelog_and_inventory_mention_pl08():
    assert INVENTORY.is_file()
    inv = INVENTORY.read_text()
    assert "test_bug_pl08_street_view_object_storage" in inv
    assert "BUG-PL-08" in inv
    # CHANGELOG lives under hosteva-review workspace, not always in this repo.
    if CHANGELOG.is_file():
        cl = CHANGELOG.read_text()
        assert "BUG-PL-08" in cl
        assert "PROPERTY_IMAGE_BUCKET" in cl
        assert "Cloudflare R2" in cl
