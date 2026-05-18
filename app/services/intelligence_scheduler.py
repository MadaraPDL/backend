from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.isp import ISP
from app.services.isp_admin import run_intelligence_for_isp

logger = logging.getLogger(__name__)

_scheduler_task: asyncio.Task[None] | None = None


async def run_intelligence_for_all_isps_once() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ISP.id).where(ISP.status == "active").order_by(ISP.created_at.desc())
        )
        isp_ids = list(result.scalars().all())

        for isp_id in isp_ids:
            try:
                run_result = await run_intelligence_for_isp(db=db, isp_id=isp_id)
                logger.info(
                    "PulseFi intelligence run completed for ISP %s: checked=%s predictions=%s recommendations=%s skipped=%s failed=%s",
                    isp_id,
                    run_result.subscriptions_checked,
                    run_result.predictions_created,
                    run_result.recommendations_created,
                    run_result.skipped,
                    run_result.failed,
                )
            except Exception:
                logger.exception("PulseFi intelligence run failed for ISP %s", isp_id)

        await db.commit()


async def intelligence_scheduler_loop() -> None:
    interval_seconds = max(
        60,
        settings.INTELLIGENCE_SCHEDULER_INTERVAL_MINUTES * 60,
    )

    logger.info(
        "PulseFi intelligence scheduler started. interval_seconds=%s",
        interval_seconds,
    )

    while True:
        try:
            logger.info(
                "PulseFi intelligence scheduler tick at %s",
                datetime.now(timezone.utc).isoformat(),
            )
            await run_intelligence_for_all_isps_once()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("PulseFi intelligence scheduler tick failed")

        await asyncio.sleep(interval_seconds)


def start_intelligence_scheduler() -> None:
    global _scheduler_task

    if not settings.ENABLE_INTELLIGENCE_SCHEDULER:
        logger.info("PulseFi intelligence scheduler disabled.")
        return

    if _scheduler_task is not None and not _scheduler_task.done():
        return

    _scheduler_task = asyncio.create_task(intelligence_scheduler_loop())


async def stop_intelligence_scheduler() -> None:
    global _scheduler_task

    if _scheduler_task is None:
        return

    _scheduler_task.cancel()

    with suppress(asyncio.CancelledError):
        await _scheduler_task

    _scheduler_task = None
    logger.info("PulseFi intelligence scheduler stopped.")
