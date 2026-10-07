"""Тесты логики: слоты, телефон, формат даты. Не требуют сети и Telegram."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from content import WORK_END_HOUR, WORK_START_HOUR
from utils import all_slots, format_date_ru, free_slots, is_valid_phone, normalize_phone


def test_all_slots_from_open_to_before_close() -> None:
    slots = all_slots()
    assert slots[0] == f"{WORK_START_HOUR:02d}:00"
    assert slots[-1] == f"{WORK_END_HOUR - 1:02d}:00"
    assert len(slots) == WORK_END_HOUR - WORK_START_HOUR


def test_free_slots_excludes_busy() -> None:
    slots = all_slots()
    busy = {slots[0], slots[2]}
    result = free_slots(busy)
    assert slots[0] not in result
    assert slots[2] not in result
    assert slots[1] in result


def test_valid_phone_variants() -> None:
    assert is_valid_phone("+7 900 000-00-00")
    assert is_valid_phone("89000000000")
    assert is_valid_phone("(999) 123-45-67")
    assert not is_valid_phone("abc")
    assert not is_valid_phone("123")


def test_normalize_phone_trims() -> None:
    assert normalize_phone("  +7 900 000-00-00  ") == "+7 900 000-00-00"


def test_format_date_ru() -> None:
    assert format_date_ru("2026-10-07") == "7 октября"
    assert format_date_ru("2026-01-01") == "1 января"
