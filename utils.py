"""Утилиты: слоты времени, форматирование, валидация телефона."""

from __future__ import annotations

import re
from datetime import date

from content import WORK_END_HOUR, WORK_START_HOUR

_PHONE_RE = re.compile(r"^\+?[\d\s\-()]{10,18}$")


def all_slots() -> list[str]:
    """Все часовые слоты рабочего дня, напр. 10:00 … 19:00."""
    return [f"{h:02d}:00" for h in range(WORK_START_HOUR, WORK_END_HOUR)]


def free_slots(busy_times: set[str]) -> list[str]:
    return [t for t in all_slots() if t not in busy_times]


def is_valid_phone(raw: str) -> bool:
    return bool(_PHONE_RE.match(raw.strip()))


def normalize_phone(raw: str) -> str:
    return raw.strip()


def format_date_ru(date_iso: str) -> str:
    d = date.fromisoformat(date_iso)
    months = (
        "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря",
    )
    return f"{d.day} {months[d.month - 1]}"
