"""Слой доступа к данным на SQLite (aiosqlite). Никаких ORM — просто и понятно."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import aiosqlite

from config import settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY,
    username    TEXT,
    full_name   TEXT,
    phone       TEXT,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bookings (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    client_name  TEXT NOT NULL,
    phone        TEXT NOT NULL,
    service_id   TEXT NOT NULL,
    service_name TEXT NOT NULL,
    price        INTEGER NOT NULL,
    date         TEXT NOT NULL,   -- YYYY-MM-DD
    time         TEXT NOT NULL,   -- HH:MM
    master       TEXT,
    status       TEXT NOT NULL DEFAULT 'new',
    created_at   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_bookings_slot ON bookings (date, time, status);
"""


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


async def init_db() -> None:
    async with aiosqlite.connect(settings.db_path) as db:
        await db.executescript(_SCHEMA)
        await db.commit()


async def save_user(user_id: int, username: str | None, full_name: str | None) -> None:
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(
            """
            INSERT INTO users (id, username, full_name, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                username = excluded.username,
                full_name = excluded.full_name
            """,
            (user_id, username, full_name, _now()),
        )
        await db.commit()


async def is_slot_taken(date: str, time: str) -> bool:
    async with aiosqlite.connect(settings.db_path) as db:
        cursor = await db.execute(
            """
            SELECT 1 FROM bookings
            WHERE date = ? AND time = ? AND status != 'cancelled'
            LIMIT 1
            """,
            (date, time),
        )
        return await cursor.fetchone() is not None


async def add_booking(
    *,
    user_id: int,
    client_name: str,
    phone: str,
    service_id: str,
    service_name: str,
    price: int,
    date: str,
    time: str,
    master: str | None = None,
) -> int:
    async with aiosqlite.connect(settings.db_path) as db:
        cursor = await db.execute(
            """
            INSERT INTO bookings
                (user_id, client_name, phone, service_id, service_name,
                 price, date, time, master, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', ?)
            """,
            (
                user_id, client_name, phone, service_id, service_name,
                price, date, time, master, _now(),
            ),
        )
        await db.commit()
        return int(cursor.lastrowid)


async def get_user_bookings(user_id: int) -> list[dict[str, Any]]:
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT * FROM bookings
            WHERE user_id = ? AND status != 'cancelled'
            ORDER BY date, time
            """,
            (user_id,),
        )
        return [dict(row) for row in await cursor.fetchall()]


async def get_bookings_by_date(date: str) -> list[dict[str, Any]]:
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM bookings WHERE date = ? AND status != 'cancelled' ORDER BY time",
            (date,),
        )
        return [dict(row) for row in await cursor.fetchall()]


async def get_booking(booking_id: int) -> dict[str, Any] | None:
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def cancel_booking(booking_id: int) -> bool:
    async with aiosqlite.connect(settings.db_path) as db:
        cursor = await db.execute(
            "UPDATE bookings SET status = 'cancelled' WHERE id = ? AND status != 'cancelled'",
            (booking_id,),
        )
        await db.commit()
        return cursor.rowcount > 0


async def set_status(booking_id: int, status: str) -> None:
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute("UPDATE bookings SET status = ? WHERE id = ?", (status, booking_id))
        await db.commit()
