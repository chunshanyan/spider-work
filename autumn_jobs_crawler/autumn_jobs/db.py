from __future__ import annotations

import os
import pathlib
from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    create_engine,
    String,
    Text,
    Integer,
    Date,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


DEFAULT_DB_PATH = os.environ.get(
    "AUTUMN_JOBS_DB",
    "/workspace/autumn_jobs_crawler/data/jobs.db",
)


class Base(DeclarativeBase):
    pass


class JobPosting(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("company", "job_title", "url", name="uq_company_title_url"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    company: Mapped[str] = mapped_column(String(255), nullable=False)
    company_size_category: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    job_title: Mapped[str] = mapped_column(String(512), nullable=False)

    job_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    job_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    publish_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    deadline: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    education_requirement: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    source_site: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


_engine = None
_SessionLocal = None


def _ensure_parent_dir(path: str) -> None:
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)


def get_engine():
    global _engine
    if _engine is None:
        _ensure_parent_dir(DEFAULT_DB_PATH)
        _engine = create_engine(f"sqlite:///{DEFAULT_DB_PATH}", echo=False, future=True)
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)
    return _SessionLocal


def init_db() -> None:
    engine = get_engine()
    Base.metadata.create_all(engine)