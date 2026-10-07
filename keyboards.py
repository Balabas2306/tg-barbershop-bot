"""Клавиатуры бота. Всё на inline-кнопках — выглядит аккуратно в демо."""

from __future__ import annotations

from datetime import date, timedelta

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from content import SERVICES


def main_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✂️ Записаться", callback_data="book")
    kb.button(text="📋 Мои записи", callback_data="my")
    kb.button(text="💈 Услуги и цены", callback_data="services")
    kb.button(text="📍 Контакты", callback_data="contacts")
    kb.adjust(2, 2)
    return kb.as_markup()


def services_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for s in SERVICES:
        kb.button(text=f"{s.name} — {s.price} ₽", callback_data=f"svc:{s.id}")
    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def dates_kb(days: int = 7) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    today = date.today()
    weekdays = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")
    for i in range(days):
        d = today + timedelta(days=i)
        label = "Сегодня" if i == 0 else ("Завтра" if i == 1 else f"{weekdays[d.weekday()]}, {d.day:02d}.{d.month:02d}")
        kb.button(text=label, callback_data=f"date:{d.isoformat()}")
    kb.button(text="⬅️ Назад", callback_data="book")
    kb.adjust(2)
    return kb.as_markup()


def times_kb(date_iso: str, free_slots: list[str]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if not free_slots:
        kb.button(text="На этот день мест нет", callback_data="noop")
    for t in free_slots:
        kb.button(text=t, callback_data=f"time:{date_iso}:{t}")
    kb.button(text="⬅️ Другая дата", callback_data="book")
    kb.adjust(3)
    return kb.as_markup()


def masters_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="👤 Любой мастер", callback_data="master:any")
    for m in ("Алексей", "Дмитрий", "Артём"):
        kb.button(text=m, callback_data=f"master:{m}")
    kb.button(text="⬅️ Назад", callback_data="book")
    kb.adjust(2)
    return kb.as_markup()


def confirm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить запись", callback_data="confirm")
    kb.button(text="❌ Отмена", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def cancel_input_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ В меню", callback_data="menu")
    return kb.as_markup()


def my_bookings_kb(bookings: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for b in bookings:
        kb.button(
            text=f"❌ {b['date']} {b['time']} — отменить",
            callback_data=f"cancel:{b['id']}",
        )
    kb.button(text="⬅️ В меню", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def admin_decision_kb(booking_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data=f"adone:{booking_id}")
    kb.button(text="🚫 Отклонить", callback_data=f"adrop:{booking_id}")
    kb.adjust(2)
    return kb.as_markup()
