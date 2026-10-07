# 💈 Демо-бот барбершопа (Python + aiogram 3)

Портфолио-проект для трека «Telegram-боты под заказ».
Показывает полный сценарий онлайн-записи + админку мастера.

## Что умеет

- **/start** — меню: записаться, мои записи, услуги и цены, контакты.
- **Запись за 30 секунд:** услуга → дата (7 дней) → свободное время → имя →
  телефон → мастер → подтверждение.
- **Свободные слоты** считаются из базы: занятое время не показывается.
- **Мои записи** — список + отмена в один клик.
- **Админка:** новая запись приходит мастеру (ADMIN_ID), он подтверждает или
  отклоняет, клиенту уходит уведомление.
- SQLite, чистые слои (`config / content / db / keyboards / handlers`).

## Запуск

```powershell
cd C:\Users\Roman\Desktop\Заработок\demo-bot-barbershop
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

copy .env.example .env
# откройте .env: BOT_TOKEN (от @BotFather), ADMIN_ID (ваш Telegram ID)
.\.venv\Scripts\python.exe bot.py
```

## Тесты

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Тесты покрывают логику слотов, валидацию телефона и работу БД
(`tests/`).

## Как это продавать клиенту

1. Показать бота вживую (это демо — уже продающий аргумент).
2. Заменить `content.py` (услуги, цены, контакты) и `SHOP_NAME` в `.env`.
3. Деплой на VPS (Timeweb/Selectel ~200–400 ₽/мес), systemd-юнит + автозапуск.
4. По желанию: напоминание за 2 ч (APScheduler), оплата (ЮKassa/Stars),
   Google-таблица, экспорт выгрузок.

## Стек

aiogram 3.15 · aiosqlite · SQLite · python-dotenv
