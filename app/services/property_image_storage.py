"""BUG-PL-08 — S3-compatible object storage for Street View / Places JPGs.

Default provider: Cloudflare R2 (S3 API). AWS S3 also supported via env.

Env (names only — do not commit secret values):
  PROPERTY_IMAGE_PROVIDER          r2 (default) | s3
  PROPERTY_IMAGE_BUCKET            bucket name
  PROPERTY_IMAGE_ENDPOINT_URL      required for R2 (https://<accountid>.r2.cloudflarestorage.com)
  PROPERTY_IMAGE_REGION            default auto (R2) or e.g. us-east-1 (S3)
  PROPERTY_IMAGE_ACCESS_KEY_ID     access key (secret-request card)
  PROPERTY_IMAGE_SECRET_ACCESS_KEY secret key (secret-request card)
  PROPERTY_IMAGE_PUBLIC_BASE_URL   durable HTTPS prefix written to DB
                                   (e.g. https://images.gethosteva.com or R2 public URL)
  PROPERTY_IMAGE_KEY_PREFIX        optional key prefix (default property-images/)
  PROPERTY_IMAGE_LAZY_VERIFY       if true/1, HEAD-check HTTPS URLs on list heal path

fallback_house.jpg stays in app static — never uploaded here.
"""
from __future__ import annotations

import logging
import os
import uuid
from typing import Optional
from urllib.parse import urljoin

logger = logging.getLogger("app.services.property_image_storage")

DEFAULT_KEY_PREFIX = "property-images/"


def _env(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()


def provider_name() -> str:
    return (_env("PROPERTY_IMAGE_PROVIDER", "r2") or "r2").lower()


def storage_configured() -> bool:
    """True when bucket + credentials + public base are set for upload."""
    return bool(
        _env("PROPERTY_IMAGE_BUCKET")
        and _env("PROPERTY_IMAGE_ACCESS_KEY_ID")
        and _env("PROPERTY_IMAGE_SECRET_ACCESS_KEY")
        and _env("PROPERTY_IMAGE_PUBLIC_BASE_URL")
    )


def _public_base() -> str:
    base = _env("PROPERTY_IMAGE_PUBLIC_BASE_URL").rstrip("/") + "/"
    return base


def _key_prefix() -> str:
    prefix = _env("PROPERTY_IMAGE_KEY_PREFIX", DEFAULT_KEY_PREFIX)
    if prefix and not prefix.endswith("/"):
        prefix += "/"
    return prefix or DEFAULT_KEY_PREFIX


def _region() -> str:
    default = "auto" if provider_name() == "r2" else "us-east-1"
    return _env("PROPERTY_IMAGE_REGION", default) or default


def _endpoint_url() -> Optional[str]:
    endpoint = _env("PROPERTY_IMAGE_ENDPOINT_URL")
    if endpoint:
        return endpoint
    # AWS S3 can omit endpoint (boto3 regional). R2 requires it.
    if provider_name() == "r2":
        return None
    return None


def _client():
    """Lazy boto3 S3 client — import only when uploading."""
    import boto3
    from botocore.config import Config

    kwargs = {
        "service_name": "s3",
        "aws_access_key_id": _env("PROPERTY_IMAGE_ACCESS_KEY_ID"),
        "aws_secret_access_key": _env("PROPERTY_IMAGE_SECRET_ACCESS_KEY"),
        "region_name": _region(),
        "config": Config(signature_version="s3v4"),
    }
    endpoint = _endpoint_url()
    if endpoint:
        kwargs["endpoint_url"] = endpoint
    elif provider_name() == "r2":
        raise RuntimeError(
            "PROPERTY_IMAGE_ENDPOINT_URL is required when PROPERTY_IMAGE_PROVIDER=r2"
        )
    return boto3.client(**kwargs)


def build_public_url(object_key: str) -> str:
    """Compose durable HTTPS URL from public base + object key."""
    key = object_key.lstrip("/")
    return urljoin(_public_base(), key)


def upload_property_image(content: bytes, *, content_type: str = "image/jpeg") -> str:
    """Upload JPG bytes to object storage; return durable HTTPS URL.

    Raises RuntimeError if storage is not configured or upload fails.
    """
    if not content:
        raise ValueError("empty image content")
    if not storage_configured():
        raise RuntimeError("property image object storage is not configured")

    object_key = f"{_key_prefix()}{uuid.uuid4()}.jpg"
    bucket = _env("PROPERTY_IMAGE_BUCKET")
    client = _client()
    extra = {
        "ContentType": content_type,
        "CacheControl": "public, max-age=31536000, immutable",
    }
    # Public-read ACL is optional; prefer bucket policy / R2 public access.
    # Do not set ACL unless explicitly requested (R2 often ignores ACLs).
    acl = _env("PROPERTY_IMAGE_OBJECT_ACL")
    put_kwargs = {
        "Bucket": bucket,
        "Key": object_key,
        "Body": content,
        **extra,
    }
    if acl:
        put_kwargs["ACL"] = acl

    client.put_object(**put_kwargs)
    url = build_public_url(object_key)
    logger.info(
        "BUG-PL-08: uploaded property image key=%s provider=%s url=%s",
        object_key,
        provider_name(),
        url,
    )
    return url


def remote_image_ok(url: str, *, timeout: float = 1.5) -> bool:
    """HEAD the URL; True only on HTTP 200."""
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        return False
    try:
        import requests

        resp = requests.head(url, timeout=timeout, allow_redirects=True)
        if resp.status_code == 200:
            return True
        # Some stores reject HEAD — try a ranged GET
        if resp.status_code in (403, 405):
            resp = requests.get(
                url,
                timeout=timeout,
                allow_redirects=True,
                headers={"Range": "bytes=0-0"},
            )
            return resp.status_code in (200, 206)
        return False
    except Exception:
        logger.info("BUG-PL-08: remote image check failed for %s", url, exc_info=True)
        return False
