"""
Stage 2 Normalizer: Date Parser
Normalizes relative and absolute dates into timezone-aware ISO-8601 datetimes.
Supports reference time injection for deterministic testing.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
import re
import logging

logger = logging.getLogger("DateParser")


class DateParser:
    """Parses relative and absolute date strings into UTC ISO-8601 datetime objects."""

    @classmethod
    def parse(
        cls,
        raw_date: Optional[str],
        reference_time: Optional[datetime] = None
    ) -> Optional[datetime]:
        """
        Parses date string into a timezone-aware UTC datetime.
        Returns None if date is unknown or unparseable (never fabricates current date for missing input).
        """
        if not raw_date or not isinstance(raw_date, str):
            return None

        d_str = raw_date.strip().lower()
        now = reference_time or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        # 1. Immediate Relative Terms
        if d_str in ["just now", "today", "few seconds ago", "moment ago"]:
            return now
        if d_str in ["yesterday", "1 day ago"]:
            return now - timedelta(days=1)

        # 2. Relative "X hours/days/weeks/months ago"
        rel_match = re.search(r"(\d+)\s*(hour|day|week|month|hr)s?\s*ago", d_str)
        if rel_match:
            amount = int(rel_match.group(1))
            unit = rel_match.group(2)
            if unit in ["hour", "hr"]:
                return now - timedelta(hours=amount)
            elif unit == "day":
                return now - timedelta(days=amount)
            elif unit == "week":
                return now - timedelta(weeks=amount)
            elif unit == "month":
                return now - timedelta(days=amount * 30)

        # 3. ISO-8601 (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        iso_match = re.search(r"(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2}):(\d{2}))?", d_str)
        if iso_match:
            try:
                y, m, d = int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))
                hh = int(iso_match.group(4) or 0)
                mm = int(iso_match.group(5) or 0)
                ss = int(iso_match.group(6) or 0)
                return datetime(y, m, d, hh, mm, ss, tzinfo=timezone.utc)
            except ValueError:
                pass

        # 4. Standard Slash / Dash format (DD/MM/YYYY or DD-MM-YYYY)
        dmy_match = re.search(r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})", d_str)
        if dmy_match:
            try:
                d, m, y = int(dmy_match.group(1)), int(dmy_match.group(2)), int(dmy_match.group(3))
                return datetime(y, m, d, 0, 0, 0, tzinfo=timezone.utc)
            except ValueError:
                pass

        # 5. Month DD, YYYY (e.g., October 13, 2026 or Oct 13, 2026)
        for fmt in ["%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y"]:
            try:
                dt = datetime.strptime(raw_date.strip(), fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue

        # Unknown format
        return None
