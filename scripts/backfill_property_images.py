#!/usr/bin/env python3
"""One-shot CLI for BUG-PL-08 property image backfill (ephemeral → object storage).

Safe to re-run. Prefer admin endpoint in prod:
  POST /api/v1/admin/properties/backfill-images

Usage:
  python scripts/backfill_property_images.py
  python scripts/backfill_property_images.py --host-id HOST_UUID
  python scripts/backfill_property_images.py --limit 16
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


def main() -> int:
    parser = argparse.ArgumentParser(description="BUG-PL-08 property image backfill")
    parser.add_argument("--host-id", default=None, help="Limit to one host")
    parser.add_argument("--limit", type=int, default=None, help="Max rows to scan")
    parser.add_argument(
        "--no-verify-remote",
        action="store_true",
        help="Skip HEAD checks on existing HTTPS URLs",
    )
    parser.add_argument(
        "--include-placeholders",
        action="store_true",
        default=None,
        help="Retry placeholder rows (default when storage configured)",
    )
    parser.add_argument(
        "--skip-placeholders",
        action="store_true",
        help="Never retry fallback_house.jpg / empty rows",
    )
    args = parser.parse_args()

    from app.database import SessionLocal
    from app.services.property_image_heal import backfill_property_images

    include_placeholders = None
    if args.skip_placeholders:
        include_placeholders = False
    elif args.include_placeholders:
        include_placeholders = True

    db = SessionLocal()
    try:
        result = backfill_property_images(
            db,
            host_id=args.host_id,
            limit=args.limit,
            verify_remote=not args.no_verify_remote,
            include_placeholders=include_placeholders,
        )
        print(json.dumps({"ok": True, **result.to_dict()}, indent=2))
        return 0 if not result.errors else 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
