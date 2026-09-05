"""TE-005: purge labeled sample/demo ordinances (production)."""
import os
import logging

logger = logging.getLogger(__name__)


def purge_sample_ordinances() -> int:
    if os.getenv("ENVIRONMENT", "").lower() != "production":
        return 0
    try:
        from app.database import SessionLocal
        from app.models.compliance import Ordinance

        db = SessionLocal()
        try:
            n = (
                db.query(Ordinance)
                .filter(
                    (Ordinance.jurisdiction.ilike("%sample%"))
                    | (Ordinance.jurisdiction.ilike("%demo%"))
                )
                .delete(synchronize_session=False)
            )
            db.commit()
            logger.info("Purged %s sample/demo ordinance row(s)", n)
            print(f"Purged {n} sample/demo ordinance row(s)")
            return n or 0
        finally:
            db.close()
    except Exception as e:
        logger.exception("Sample ordinance purge skipped: %s", e)
        print(f"Sample ordinance purge skipped: {e}")
        return 0


if __name__ == "__main__":
    purge_sample_ordinances()
