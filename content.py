"""Контент барбершопа: услуги, мастера, тексты. Легко правится под клиента."""

from __future__ import annotations

import os
from dataclasses import dataclass

SHOP_NAME = os.getenv("SHOP_NAME", "Барбершоп «Клинок»")


@dataclass(frozen=True)
class Service:
    id: str
    name: str
    price: int  # ₽
    duration: str


SERVICES: tuple[Service, ...] = (
    Service("haircut", "Мужская стрижка", 1200, "45 мин"),
    Service("fade", "Стрижка машинкой (fade)", 900, "30 мин"),
    Service("beard", "Оформление бороды", 700, "25 мин"),
    Service("combo", "Стрижка + борода", 1700, "70 мин"),
    Service("kids", "Детская стрижка", 800, "30 мин"),
    Service("shave", "Королевское бритьё", 1000, "40 мин"),
)

SERVICES_BY_ID: dict[str, Service] = {s.id: s for s in SERVICES}

# Часы работы: слоты по часу, последний слот — за час до закрытия
WORK_START_HOUR = 10
WORK_END_HOUR = 20  # закрытие; последняя запись в 19:00

MASTERS = ("Алексей", "Дмитрий", "Артём")

CONTACTS_TEXT = (
    f"📍 {SHOP_NAME}\n"
    "г. Курск, ул. Примерная, 12\n"
    "🕙 Ежедневно с 10:00 до 20:00\n"
    "📞 +7 (900) 000-00-00\n"
    "✂️ Работаем с 2019 года"
)
