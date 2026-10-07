"""Админ-панель: уведомления о новых записях и управление статусом."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

import db
from config import settings
from keyboards import admin_decision_kb, main_menu

router = Router(name="admin")


def _is_admin(user_id: int) -> bool:
    return user_id == settings.admin_id


def booking_card(b: dict, *, header: str) -> str:
    return (
        f"{header}\n\n"
        f"№{b['id']}\n"
        f"👤 {b['client_name']}\n"
        f"📞 {b['phone']}\n"
        f"✂️ {b['service_name']} — {b['price']} ₽\n"
        f"📅 {b['date']} в {b['time']}\n"
        f"💈 Мастер: {b.get('master') or 'любой'}"
    )


@router.callback_query(F.data.startswith("adone:"))
async def admin_confirm(callback: CallbackQuery) -> None:
    if not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    booking_id = int((callback.data or "").split(":", 1)[1])
    b = await db.get_booking(booking_id)
    if not b or b["status"] != "new":
        await callback.answer("Уже обработано", show_alert=True)
        return

    await db.set_status(booking_id, "confirmed")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer("Подтверждено")
    await callback.bot.send_message(
        b["user_id"],
        f"✅ Ваша запись подтверждена!\n\n"
        f"✂️ {b['service_name']}\n"
        f"📅 {b['date']} в {b['time']}\n"
        f"💈 Мастер: {b.get('master') or 'любой'}\n\n"
        f"Ждём вас в {settings.shop_name}!",
    )


@router.callback_query(F.data.startswith("adrop:"))
async def admin_reject(callback: CallbackQuery) -> None:
    if not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    booking_id = int((callback.data or "").split(":", 1)[1])
    b = await db.get_booking(booking_id)
    if not b or b["status"] != "new":
        await callback.answer("Уже обработано", show_alert=True)
        return

    await db.set_status(booking_id, "rejected")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer("Отклонено")
    await callback.bot.send_message(
        b["user_id"],
        f"😔 К сожалению, запись на {b['date']} {b['time']} не подтверждена.\n"
        f"Попробуйте выбрать другое время: /start",
    )
