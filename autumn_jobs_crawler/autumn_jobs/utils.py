from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from dateutil import parser as dateparser


def parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    if isinstance(value, (datetime, date)):
        return value.date() if isinstance(value, datetime) else value
    try:
        dt = dateparser.parse(str(value), dayfirst=False, yearfirst=True)
        if not dt:
            return None
        return dt.date()
    except Exception:
        return None


def clean_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    # Collapse multiple spaces and newlines
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    return text or None