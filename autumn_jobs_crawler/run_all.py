from __future__ import annotations

import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run_once():
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    # Register spiders here
    from autumn_jobs.spiders.tencent import TencentJobsSpider

    process.crawl(TencentJobsSpider)

    logger.info("Starting crawl run at %s", datetime.now())
    process.start()
    logger.info("Crawl run finished at %s", datetime.now())


if __name__ == "__main__":
    # Immediate run once
    run_once()

    # Daily schedule at 02:00
    # Tip: In production, prefer cron or systemd timers. Below is for dev/demo.
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(run_once, "cron", hour=2, minute=0, id="daily_crawl")

    logger.info("Scheduler started; next run at 02:00")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")