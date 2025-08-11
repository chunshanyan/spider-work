BOT_NAME = "autumn_jobs"

SPIDER_MODULES = ["autumn_jobs.spiders"]
NEWSPIDER_MODULE = "autumn_jobs.spiders"

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 0.5

DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

DOWNLOADER_MIDDLEWARES = {
    "scrapy_user_agents.middlewares.RandomUserAgentMiddleware": 400,
}

ITEM_PIPELINES = {
    "autumn_jobs.pipelines.JobNormalizeAndStorePipeline": 300,
}

FEED_EXPORT_ENCODING = "utf-8"
LOG_LEVEL = "INFO"