"""Конфигурация бота: читается из переменных окружения / .env."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class ConfigError(RuntimeError):
    """Не заданы обязательные переменные окружения."""


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admin_id: int
    shop_name: str
    db_path: Path


def load_settings() -> Settings:
    token = os.getenv("BOT_TOKEN", "").strip()
    admin_raw = os.getenv("ADMIN_ID", "").strip()
    if not token:
        raise ConfigError("BOT_TOKEN не задан. Скопируйте .env.example в .env и заполните.")
    if not admin_raw.isdigit():
        raise ConfigError("ADMIN_ID не задан или не число (Telegram ID администратора).")

    return Settings(
        bot_token=token,
        admin_id=int(admin_raw),
        shop_name=os.getenv("SHOP_NAME", "Барбершоп").strip() or "Барбершоп",
        db_path=BASE_DIR / "barbershop.db",
    )


settings = load_settings()
