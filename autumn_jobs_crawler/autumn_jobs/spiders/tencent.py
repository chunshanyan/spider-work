from __future__ import annotations

import math
import time
import urllib.parse
from typing import Any, Dict, Iterable

import scrapy

from ..items import JobItem


class TencentJobsSpider(scrapy.Spider):
    name = "tencent"
    allowed_domains = ["careers.tencent.com"]

    custom_settings = {
        # Be extra polite per-site
        "DOWNLOAD_DELAY": 0.6,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
    }

    def start_requests(self) -> Iterable[scrapy.Request]:
        # API docs are not public; this is a commonly observed endpoint.
        # We'll query campus and social posts under CN area with zh-cn language.
        base_url = "https://careers.tencent.com/tencentcareer/api/post/Query"
        page_size = 20
        params = {
            "timestamp": str(int(time.time() * 1000)),
            "countryId": "",
            "cityId": "",
            "bgIds": "",
            "postIds": "",
            "keyword": "",
            "pageIndex": "1",
            "pageSize": str(page_size),
            "language": "zh-cn",
            "area": "cn",
        }
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        yield scrapy.Request(url, callback=self.parse_listing, headers={
            "Referer": "https://careers.tencent.com/search.html",
            "Accept": "application/json, text/plain, */*",
        }, cb_kwargs={"page_size": page_size, "base_url": base_url})

    def parse_listing(self, response: scrapy.http.Response, page_size: int, base_url: str):
        data = response.json() if response.headers.get("Content-Type", b"").startswith(b"application/json") else None
        if not data:
            self.logger.warning("Unexpected response, not JSON")
            return

        # Different deployments have varied structures; handle defensively
        total = (
            data.get("Data", {}).get("Count")
            or data.get("Data", {}).get("total")
            or data.get("Count")
            or data.get("total")
            or 0
        )
        posts = (
            data.get("Data", {}).get("Posts")
            or data.get("Data", {}).get("posts")
            or data.get("Posts")
            or data.get("posts")
            or []
        )

        for post in posts:
            yield from self._yield_item(post)

        # pagination
        try:
            first_params = urllib.parse.parse_qs(urllib.parse.urlparse(response.url).query)
            current_page = int(first_params.get("pageIndex", ["1"])[0])
        except Exception:
            current_page = 1

        total_pages = int(math.ceil((total or 0) / float(page_size))) if page_size else 1
        if current_page < total_pages and current_page < 50:  # cap to avoid overly long runs
            next_params = {k: v[0] if isinstance(v, list) else v for k, v in first_params.items()}
            next_params["pageIndex"] = str(current_page + 1)
            next_params["timestamp"] = str(int(time.time() * 1000))
            next_url = f"{base_url}?{urllib.parse.urlencode(next_params)}"
            yield scrapy.Request(next_url, callback=self.parse_listing, headers={
                "Referer": "https://careers.tencent.com/search.html",
                "Accept": "application/json, text/plain, */*",
            }, cb_kwargs={"page_size": page_size, "base_url": base_url})

    def _yield_item(self, post: Dict[str, Any]):
        # Try multiple key variants to be robust
        title = post.get("RecruitPostName") or post.get("Title") or post.get("recruitPostName") or post.get("title")
        url = (
            post.get("PostURL")
            or post.get("postURL")
            or post.get("PostUrl")
            or post.get("postUrl")
            or post.get("Url")
            or post.get("url")
        )
        if url and url.startswith("/"):
            url = f"https://careers.tencent.com{url}"

        location = post.get("LocationName") or post.get("Location") or post.get("locationName") or post.get("location")
        # Some responses include requirement/description fields
        requirement = (
            post.get("Requirement")
            or post.get("requirement")
            or post.get("RecruitPostRequire")
            or post.get("Description")
            or post.get("description")
        )
        description = post.get("Responsibility") or post.get("responsibility") or post.get("Description") or post.get("description")
        last_update = post.get("LastUpdateTime") or post.get("lastUpdateTime")

        item = JobItem()
        item["company"] = "腾讯"
        item["company_size_category"] = "big"
        item["url"] = url
        item["job_title"] = title
        item["job_description"] = description
        item["job_requirements"] = requirement
        item["publish_date"] = last_update
        item["deadline"] = None
        item["education_requirement"] = None
        item["source_site"] = "careers.tencent.com"
        item["city"] = location

        yield item