from __future__ import annotations

import os
from typing import Any, Dict

from sqlalchemy.exc import IntegrityError
from scrapy.exceptions import DropItem

from .db import JobPosting, get_session_factory, init_db
from .utils import parse_date, clean_text

import yaml


class JobNormalizeAndStorePipeline:
    def __init__(self, companies_map: Dict[str, str]):
        self.companies_map = companies_map
        self.SessionLocal = get_session_factory()

    @classmethod
    def from_crawler(cls, crawler):
        # Load company size mapping
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(os.path.dirname(project_root), "config", "companies.yml")
        mapping: Dict[str, str] = {}
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
                mapping = {str(k).strip(): str(v).strip() for k, v in raw.items() if k}
        # Ensure DB tables are created
        init_db()
        return cls(mapping)

    def process_item(self, item, spider):
        company = clean_text(item.get("company"))
        url = clean_text(item.get("url"))
        job_title = clean_text(item.get("job_title"))
        job_description = clean_text(item.get("job_description"))
        job_requirements = clean_text(item.get("job_requirements"))
        education_requirement = clean_text(item.get("education_requirement"))
        source_site = clean_text(item.get("source_site"))
        city = clean_text(item.get("city"))

        publish_date = parse_date(item.get("publish_date"))
        deadline = parse_date(item.get("deadline"))

        company_size_category = item.get("company_size_category") or self.companies_map.get(company or "", "unknown")

        if not (company and url and job_title):
            spider.logger.warning("Drop item due to missing required fields: %s", {
                "company": company,
                "url": url,
                "job_title": job_title,
            })
            raise DropItem("missing required fields")

        record = JobPosting(
            company=company,
            company_size_category=company_size_category,
            url=url,
            job_title=job_title,
            job_description=job_description,
            job_requirements=job_requirements,
            publish_date=publish_date,
            deadline=deadline,
            education_requirement=education_requirement,
            source_site=source_site,
            city=city,
        )

        session = self.SessionLocal()
        try:
            session.add(record)
            session.commit()
        except IntegrityError:
            session.rollback()
            spider.logger.info("Duplicate job skipped: %s | %s | %s", company, job_title, url)
        finally:
            session.close()

        return item

# No custom DropItem class needed; using scrapy.exceptions.DropItem