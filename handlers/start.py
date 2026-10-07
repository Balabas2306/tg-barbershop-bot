"""Стартовые экраны: /start, меню, услуги, контакты, мои записи."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

import db
from config import settings
from content import CONTACTS_TEXT, SERVICES
from keyboards import cancel_input_kb, main_menu, my_bookings_kb, services_kb

router = Router(name="start")

GREETING = (
    f"💈 Добро пожаловать в {settings.shop_name}!\n\n"
    "Здесь можно записаться на стрижку за 30 секунд — без звонков.\n\n"
    "Выберите действие 👇"
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user = message.from_user
    if user:
        await db.save_user(user.id, user.username, user.full_name)
    await message.answer(GREETING, reply_markup=main_menu())


@router.callback_query(F.data == "menu")
async def to_menu(callback: CallbackQuery) -> None:
    if callback.message:
        await callback.message.edit_text(GREETING, reply_markup=main_menu())
    await callback.answer()


@router.callback_query(F.data == "services")
async def show_services(callback: CallbackQuery) -> None:
    lines = ["💈 Услуги и цены:\n"]
    for s in SERVICES:
        lines.append(f"• {s.name} — {s.price} ₽ ({s.duration})")
    if callback.message:
        await callback.message.edit_text("\n".join(lines), reply_markup=services_kb())
    await callback.answer()


@router.callback_query(F.data == "contacts")
async def show_contacts(callback: CallbackQuery) -> None:
    if callback.message:
        await callback.message.edit_text(CONTACTS_TEXT, reply_markup=main_menu())
    await callback.answer()


@router.callback_query(F.data == "my")
async def my_bookings(callback: CallbackQuery) -> None:
    bookings = await db.get_user_bookings(callback.from_user.id)
    if not bookings:
        text = "У вас пока нет активных записей.\n\nЗаписаться можно кнопкой «✂️ Записаться»."
        if callback.message:
            await callback.message.edit_text(text, reply_markup=main_menu())
        await callback.answer()
        return

    lines = ["📋 Ваши записи:\n"]
    for b in bookings:
        status = "✅ подтверждена" if b["status"] == "confirmed" else "⏳ ждёт подтверждения"
        lines.append(f"• {b['date']} {b['time']} — {b['service_name']} ({status})")
    lines.append("\nНажмите запись, чтобы отменить:")
    if callback.message:
        await callback.message.edit_text("\n".join(lines), reply_markup=my_bookings_kb(bookings))
    await callback.answer()


@router.callback_query(F.data.startswith("cancel:"))
async def cancel_my_booking(callback: CallbackQuery) -> None:
    booking_id = int((callback.data or "").split(":", 1)[1])
    booking = await db.get_booking(booking_id)
    if not booking or booking["user_id"] != callback.from_user.id:
        await callback.answer("Не найдено", show_alert=True)
        return

    ok = await db.cancel_booking(booking_id)
    await callback.answer("Запись отменена" if ok else "Уже отменена")
    await my_bookings(callback)


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery) -> None:
    await callback.answer("На этот день свободных мест нет")
