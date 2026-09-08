#!/usr/bin/env python3
"""One-shot CLI for US-018b / TE-010 duplicate property cleanup.

Safe to re-run (idempotent). Prefer admin endpoint in prod; this is for
deploy/ops and local. Does not run automatically from init_db unless
RUN_DUP_CLEANUP_ON_INIT=true is set (wired in init_db.py).

Usage:
  python scripts/dedupe_duplicate_properties.py
  python scripts/dedupe_duplicate_properties.py --host-id HOST_UUID
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# Ensure repo root on path when invoked as a script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()


def main() -> int:
    parser = argparse.ArgumentParser(description="US-018b host-scoped property dedupe")
    parser.add_argument("--host-id", default=None, help="Limit to one host")
    args = parser.parse_args()

    from app.database import SessionLocal
    from app.services.duplicate_cleanup import cleanup_all_host_duplicates

    db = SessionLocal()
    try:
        result = cleanup_all_host_duplicates(db, host_id=args.host_id)
        print(json.dumps(result.to_dict(), indent=2))
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
