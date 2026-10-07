"""Основной сценарий записи: услуга → дата → время → имя → телефон → мастер → подтверждение."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

import db
from config import settings
from content import SERVICES_BY_ID
from handlers.admin import booking_card
from keyboards import (
    admin_decision_kb,
    cancel_input_kb,
    confirm_kb,
    dates_kb,
    main_menu,
    masters_kb,
    services_kb,
    times_kb,
)
from utils import format_date_ru, free_slots, is_valid_phone, normalize_phone

router = Router(name="booking")


class Booking(StatesGroup):
    service = State()
    date = State()
    time = State()
    name = State()
    phone = State()
    master = State()
    confirm = State()


@router.callback_query(F.data == "book")
async def start_booking(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if callback.message:
        await callback.message.edit_text(
            "✂️ Выберите услугу:",
            reply_markup=services_kb(),
        )
    await state.set_state(Booking.service)
    await callback.answer()


@router.callback_query(Booking.service, F.data.startswith("svc:"))
async def choose_service(callback: CallbackQuery, state: FSMContext) -> None:
    service_id = (callback.data or "").split(":", 1)[1]
    service = SERVICES_BY_ID.get(service_id)
    if not service:
        await callback.answer("Услуга не найдена", show_alert=True)
        return

    await state.update_data(service_id=service.id, service_name=service.name, price=service.price)
    await state.set_state(Booking.date)
    if callback.message:
        await callback.message.edit_text(
            f"Выбрано: {service.name} — {service.price} ₽\n\n📅 На какой день записать?",
            reply_markup=dates_kb(),
        )
    await callback.answer()


@router.callback_query(Booking.date, F.data.startswith("date:"))
async def choose_date(callback: CallbackQuery, state: FSMContext) -> None:
    date_iso = (callback.data or "").split(":", 1)[1]
    busy = {b["time"] for b in await db.get_bookings_by_date(date_iso)}
    slots = free_slots(busy)

    await state.update_data(date=date_iso)
    await state.set_state(Booking.time)
    if callback.message:
        await callback.message.edit_text(
            f"📅 {format_date_ru(date_iso)}\n\n⏰ Выберите время:",
            reply_markup=times_kb(date_iso, slots),
        )
    await callback.answer()


@router.callback_query(Booking.time, F.data.startswith("time:"))
async def choose_time(callback: CallbackQuery, state: FSMContext) -> None:
    _, date_iso, time_ = (callback.data or "").split(":", 2)
    if await db.is_slot_taken(date_iso, time_):
        await callback.answer("Это время только что заняли, выберите другое", show_alert=True)
        return

    await state.update_data(date=date_iso, time=time_)
    await state.set_state(Booking.name)
    if callback.message:
        await callback.message.edit_text(
            "👤 Как вас зовут? Напишите имя.",
            reply_markup=cancel_input_kb(),
        )
    await callback.answer()


@router.message(Booking.name)
async def enter_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer("Пожалуйста, напишите имя текстом (минимум 2 буквы).")
        return
    await state.update_data(client_name=name[:80])
    await state.set_state(Booking.phone)
    await message.answer(
        "📞 Оставьте номер телефона для связи (например, +7 900 000-00-00).",
        reply_markup=cancel_input_kb(),
    )


@router.message(Booking.phone)
async def enter_phone(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    if not is_valid_phone(raw):
        await message.answer("Похоже, номер неверный. Попробуйте ещё раз, например: +7 900 000-00-00")
        return
    await state.update_data(phone=normalize_phone(raw))
    await state.set_state(Booking.master)
    await message.answer("💈 Выберите мастера:", reply_markup=masters_kb())


@router.callback_query(Booking.master, F.data.startswith("master:"))
async def choose_master(callback: CallbackQuery, state: FSMContext) -> None:
    master = (callback.data or "").split(":", 1)[1]
    await state.update_data(master=None if master == "any" else master)
    await state.set_state(Booking.confirm)

    data = await state.get_data()
    summary = (
        "Проверьте детали записи:\n\n"
        f"✂️ {data['service_name']} — {data['price']} ₽\n"
        f"📅 {format_date_ru(data['date'])} в {data['time']}\n"
        f"👤 {data['client_name']}, {data['phone']}\n"
        f"💈 Мастер: {data.get('master') or 'любой'}"
    )
    if callback.message:
        await callback.message.edit_text(summary, reply_markup=confirm_kb())
    await callback.answer()


@router.callback_query(Booking.confirm, F.data == "confirm")
async def confirm_booking(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    if await db.is_slot_taken(data["date"], data["time"]):
        await callback.answer("Это время уже занято, начните заново", show_alert=True)
        await state.clear()
        return

    booking_id = await db.add_booking(
        user_id=callback.from_user.id,
        client_name=data["client_name"],
        phone=data["phone"],
        service_id=data["service_id"],
        service_name=data["service_name"],
        price=data["price"],
        date=data["date"],
        time=data["time"],
        master=data.get("master"),
    )
    await state.clear()

    if callback.message:
        await callback.message.edit_text(
            f"✅ Заявка №{booking_id} отправлена!\n\n"
            f"✂️ {data['service_name']}\n"
            f"📅 {format_date_ru(data['date'])} в {data['time']}\n\n"
            "Мастер подтвердит запись в ближайшее время. Напоминание придёт за 2 часа.",
            reply_markup=main_menu(),
        )

    booking = await db.get_booking(booking_id)
    if booking:
        await callback.bot.send_message(
            settings.admin_id,
            booking_card(booking, header="🔔 Новая запись!"),
            reply_markup=admin_decision_kb(booking_id),
        )
    await callback.answer("Записано!")
