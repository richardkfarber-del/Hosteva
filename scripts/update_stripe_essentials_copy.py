#!/usr/bin/env python3
"""Idempotent Stripe Product description update for Compliance Essentials (BUG-LAUNCH-01).

Requires STRIPE_SECRET_KEY. Resolves Products from:
  STRIPE_PRICE_ESSENTIALS_MONTHLY / STRIPE_PRICE_COMPLIANCE_ESSENTIALS / STRIPE_PRICE_BASIC
  STRIPE_PRICE_ESSENTIALS_YEARLY / STRIPE_PRICE_PREMIUM
  optional STRIPE_PRODUCT_ESSENTIALS

Sets Product.description (and name if empty) to Phase I honest copy.
Does not change prices, billing flags, or create new Products.

Usage:
  STRIPE_SECRET_KEY=sk_... python scripts/update_stripe_essentials_copy.py
  STRIPE_SECRET_KEY=sk_... python scripts/update_stripe_essentials_copy.py --dry-run
"""
from __future__ import annotations

import argparse
import os
import sys

# Allow running from repo root without installing package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.billing_gate import ESSENTIALS_PRODUCT_DESCRIPTION  # noqa: E402

ESSENTIALS_PRODUCT_NAME = "Hosteva Compliance Essentials"

PRICE_ENV_KEYS = (
    "STRIPE_PRICE_ESSENTIALS_MONTHLY",
    "STRIPE_PRICE_COMPLIANCE_ESSENTIALS",
    "STRIPE_PRICE_BASIC",
    "STRIPE_PRICE_ESSENTIALS_YEARLY",
    "STRIPE_PRICE_PREMIUM",
)


def _collect_product_ids(stripe) -> set[str]:
    ids: set[str] = set()
    explicit = (os.environ.get("STRIPE_PRODUCT_ESSENTIALS") or "").strip()
    if explicit:
        ids.add(explicit)
    for key in PRICE_ENV_KEYS:
        price_id = (os.environ.get(key) or "").strip()
        if not price_id or price_id.startswith("price_mock"):
            continue
        try:
            price = stripe.Price.retrieve(price_id)
            prod = price.get("product") if isinstance(price, dict) else getattr(price, "product", None)
            if prod:
                ids.add(str(prod))
                print(f"  {key}={price_id} → product {prod}")
        except Exception as e:
            print(f"  WARN: could not resolve {key}={price_id}: {e}", file=sys.stderr)
    return ids


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print planned updates only")
    args = parser.parse_args()

    key = (os.environ.get("STRIPE_SECRET_KEY") or "").strip()
    if not key:
        print("STRIPE_SECRET_KEY not set — cannot update Stripe Products.", file=sys.stderr)
        print(
            "Fallback: edit Compliance Essentials Product description in Stripe Dashboard to:\n"
            f"  {ESSENTIALS_PRODUCT_DESCRIPTION}",
            file=sys.stderr,
        )
        return 1

    import stripe

    stripe.api_key = key
    print("Resolving Essentials Product IDs from price env…")
    product_ids = _collect_product_ids(stripe)
    if not product_ids:
        print("No Product IDs found. Set STRIPE_PRODUCT_ESSENTIALS or Essentials price env vars.", file=sys.stderr)
        return 1

    target_desc = ESSENTIALS_PRODUCT_DESCRIPTION
    updated = 0
    for pid in sorted(product_ids):
        prod = stripe.Product.retrieve(pid)
        name = prod.get("name") if isinstance(prod, dict) else getattr(prod, "name", "")
        desc = prod.get("description") if isinstance(prod, dict) else getattr(prod, "description", None)
        print(f"\nProduct {pid}: name={name!r}")
        print(f"  current description: {desc!r}")
        if desc == target_desc:
            print("  already Phase I — skip")
            continue
        if args.dry_run:
            print(f"  DRY-RUN would set description → {target_desc!r}")
            continue
        kwargs = {"description": target_desc}
        # Keep existing name; only set name if blank
        if not (name or "").strip():
            kwargs["name"] = ESSENTIALS_PRODUCT_NAME
        stripe.Product.modify(pid, **kwargs)
        print(f"  updated description → {target_desc!r}")
        updated += 1

    print(f"\nDone. Products updated: {updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
