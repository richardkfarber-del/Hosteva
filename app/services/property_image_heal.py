"""BUG-PL-08 C — Lazy re-fetch / migrate property images into object storage.

Heal rules:
- Placeholder (fallback_house.jpg / empty): leave alone on hot-path list heal
  (fail-closed honesty). Admin/backfill retries placeholders when object storage
  is configured (Street View re-fetch → R2/S3 upload) so fail-closed rows can
  recover after credentials/config are fixed.
- Ephemeral `/static/property_images/*`: always migrate or re-fetch into object store.
- Durable HTTPS: trust on hot path unless PROPERTY_IMAGE_LAZY_VERIFY is set;
  admin/backfill always verifies.
- Missing local file or failed Maps re-fetch → fail-closed to placeholder.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, List, Optional

from sqlalchemy.orm import Session

logger = logging.getLogger("app.services.property_image_heal")

FALLBACK_PROPERTY_IMAGE_URL = "/static/img/fallback_house.jpg"
EPHEMERAL_PREFIX = "/static/property_images/"


def _env_truthy(name: str) -> bool:
    return (os.getenv(name) or "").strip().lower() in ("1", "true", "yes", "on")


def is_fallback_property_image(url: Optional[str]) -> bool:
    if not url:
        return True
    return "fallback_house.jpg" in url


def local_disk_path_for_url(url: str) -> Optional[str]:
    """Map `/static/...` app URL to on-disk path under app/static."""
    if not url or not url.startswith("/static/"):
        return None
    # /static/property_images/x.jpg -> app/static/property_images/x.jpg
    return "app" + url


def needs_image_heal(url: Optional[str], *, verify_remote: Optional[bool] = None) -> bool:
    """Whether this claimed non-placeholder URL should be healed/migrated."""
    if is_fallback_property_image(url):
        return False
    assert url is not None
    if url.startswith(EPHEMERAL_PREFIX):
        return True
    if url.startswith("/static/"):
        # Other static assets (not property SV) — do not treat as SV durable
        return False
    if url.startswith("http://") or url.startswith("https://"):
        do_verify = (
            _env_truthy("PROPERTY_IMAGE_LAZY_VERIFY")
            if verify_remote is None
            else verify_remote
        )
        if not do_verify:
            return False
        from app.services.property_image_storage import remote_image_ok

        return not remote_image_ok(url)
    # Unknown scheme — treat as broken claim
    return True


def _set_placeholder(prop) -> str:
    prop.image_url = FALLBACK_PROPERTY_IMAGE_URL
    return FALLBACK_PROPERTY_IMAGE_URL


def _upload_bytes(content: bytes) -> Optional[str]:
    from app.services.property_image_storage import storage_configured, upload_property_image

    if not storage_configured():
        logger.warning(
            "BUG-PL-08: object storage not configured; cannot persist Street View image"
        )
        return None
    try:
        return upload_property_image(content)
    except Exception:
        logger.exception("BUG-PL-08: object storage upload failed")
        return None


def _try_migrate_local_file(url: str) -> Optional[str]:
    """If ephemeral local file still exists, upload bytes to object store."""
    disk = local_disk_path_for_url(url)
    if not disk or not os.path.isfile(disk):
        return None
    try:
        with open(disk, "rb") as f:
            content = f.read()
        if not content:
            return None
        return _upload_bytes(content)
    except Exception:
        logger.exception("BUG-PL-08: failed reading local property image %s", disk)
        return None


def _refetch_street_view(prop) -> Optional[str]:
    """Re-fetch SV/Places via existing create-path helper; return durable URL or None."""
    from app.routers.properties import (
        FALLBACK_PROPERTY_IMAGE_URL as FB,
        fetch_real_property_image,
        is_fallback_property_image as is_fb,
    )

    parts = [
        prop.address or "",
        prop.city or "",
        f"{prop.state or ''} {prop.zip_code or ''}".strip(),
    ]
    full_address = ", ".join(p for p in parts if p).strip()
    if not full_address:
        return None
    try:
        url = fetch_real_property_image(full_address)
    except Exception:
        logger.exception("BUG-PL-08: re-fetch Street View failed for property %s", prop.id)
        return None
    if not url or is_fb(url) or url == FB:
        return None
    # fetch_real_property_image already uploads via _save_property_image_bytes
    return url


def heal_property_image(
    db: Session,
    prop,
    *,
    verify_remote: Optional[bool] = None,
    commit: bool = True,
    retry_placeholder: bool = False,
) -> str:
    """Ensure prop.image_url is durable or honest placeholder. Returns final URL.

    When ``retry_placeholder`` is True (admin/backfill only), attempt Street View
    re-fetch for rows already on fallback_house.jpg / empty image_url. Hot-path
    list heal should leave placeholders alone (default).
    """
    url = prop.image_url or ""
    if is_fallback_property_image(url):
        if not retry_placeholder:
            return url or FALLBACK_PROPERTY_IMAGE_URL
        logger.info(
            "BUG-PL-08: retrying placeholder for property %s",
            getattr(prop, "id", "?"),
        )
        refetched = _refetch_street_view(prop)
        if refetched:
            prop.image_url = refetched
            if commit:
                db.commit()
            return refetched
        # Still placeholder — leave alone (already honest)
        return url or FALLBACK_PROPERTY_IMAGE_URL

    if not needs_image_heal(url, verify_remote=verify_remote):
        return url or FALLBACK_PROPERTY_IMAGE_URL

    logger.info(
        "BUG-PL-08: healing property %s image_url=%r",
        getattr(prop, "id", "?"),
        url,
    )

    # 1) Migrate surviving local ephemeral file (no Maps cost)
    if url.startswith(EPHEMERAL_PREFIX):
        migrated = _try_migrate_local_file(url)
        if migrated:
            prop.image_url = migrated
            if commit:
                db.commit()
            return migrated

    # 2) Re-fetch Street View / Places → object store
    refetched = _refetch_street_view(prop)
    if refetched:
        prop.image_url = refetched
        if commit:
            db.commit()
        return refetched

    # 3) Fail-closed: honest placeholder (never leave claimed non-placeholder that 404s)
    final = _set_placeholder(prop)
    if commit:
        db.commit()
    logger.info(
        "BUG-PL-08: fail-closed to placeholder for property %s",
        getattr(prop, "id", "?"),
    )
    return final


@dataclass
class BackfillResult:
    scanned: int = 0
    healed: int = 0
    migrated: int = 0
    placeholders: int = 0
    skipped: int = 0
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "scanned": self.scanned,
            "healed": self.healed,
            "migrated": self.migrated,
            "placeholders": self.placeholders,
            "skipped": self.skipped,
            "errors": self.errors[:50],
        }


def backfill_property_images(
    db: Session,
    *,
    host_id: Optional[str] = None,
    limit: Optional[int] = None,
    verify_remote: bool = True,
    include_placeholders: Optional[bool] = None,
) -> BackfillResult:
    """Walk property rows and heal/migrate into object storage.

    ``include_placeholders`` defaults to True when ``storage_configured()`` so
    fail-closed placeholder rows can be retried (SV re-fetch → upload). When
    storage is not configured, placeholders stay skipped (no pointless Maps burn).
    """
    from app.models.property import Property
    from app.services.property_image_storage import storage_configured

    if include_placeholders is None:
        include_placeholders = storage_configured()

    q = db.query(Property)
    if host_id:
        q = q.filter(Property.user_id == host_id)
    props = q.all()
    result = BackfillResult()

    for prop in props:
        if limit is not None and result.scanned >= limit:
            break
        result.scanned += 1
        before = prop.image_url or ""
        is_placeholder = is_fallback_property_image(before)
        if is_placeholder and not include_placeholders:
            result.skipped += 1
            continue
        if not is_placeholder and not needs_image_heal(
            before, verify_remote=verify_remote
        ):
            result.skipped += 1
            continue
        try:
            after = heal_property_image(
                db,
                prop,
                verify_remote=verify_remote,
                commit=True,
                retry_placeholder=is_placeholder,
            )
            if is_placeholder and is_fallback_property_image(after):
                # Retry attempted but Maps/upload still failed — still placeholder
                result.skipped += 1
                continue
            if is_fallback_property_image(after):
                result.placeholders += 1
                result.healed += 1
            elif before.startswith(EPHEMERAL_PREFIX) and after.startswith("http"):
                result.migrated += 1
                result.healed += 1
            else:
                result.healed += 1
        except Exception as exc:
            logger.exception("BUG-PL-08: backfill error property %s", prop.id)
            result.errors.append(f"{prop.id}: {exc}")
            try:
                db.rollback()
            except Exception:
                pass

    return result
