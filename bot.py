import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Переменные окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))
ORDERS_TOPIC_ID = int(os.getenv("ORDERS_TOPIC_ID", "3"))
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://localhost:8443/mini-app")

# Инициализация
bot = Bot(token=TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ============= HANDLERS =============


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Обработка /start"""

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🍣 Открыть меню", web_app=WebAppInfo(url=MINI_APP_URL)
                )
            ],
            [InlineKeyboardButton(text="☎ Контакты", callback_data="contacts")],
            [InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
        ]
    )

    await message.answer(
        "🍣 Добро пожаловать в TokyoGo!\n\n"
        "Свежие суши • Только доставка • 45–60 минут\n\n"
        "Нажми кнопку ниже, чтобы открыть меню и сделать заказ!",
        reply_markup=keyboard,
    )


@dp.callback_query(F.data == "contacts")
async def contacts_callback(callback: types.CallbackQuery):
    """Показать контакты"""
    await callback.answer()
    await callback.message.answer(
        "☎ *Контакты*\n\n"
        "📱 Телефон: +7 (999) 999-99-99\n"
        "⏰ Время работы: 11:00 - 23:00\n"
        "📍 Зона доставки: центр города",
        parse_mode="Markdown",
    )


@dp.callback_query(F.data == "help")
async def help_callback(callback: types.CallbackQuery):
    """Показать помощь"""
    await callback.answer()
    await callback.message.answer(
        "❓ *Помощь*\n\n"
        "1️⃣ Нажми 'Открыть меню'\n"
        "2️⃣ Выбери товары\n"
        "3️⃣ Оформи заказ\n"
        "4️⃣ Жди доставку!\n\n"
        "Если вопросы - напиши в чат поддержки",
        parse_mode="Markdown",
    )


# ============= ФУНКЦИИ ДЛЯ УВЕДОМЛЕНИЙ =============


async def notify_admin_about_order(order_data: dict):
    """Отправить уведомление админу о новом заказе"""

    items_text = ""
    for item in order_data["items"]:
        items_text += f"• {item['name']} x{item['quantity']} = {item['price'] * item['quantity']}₽\n"

    message_text = (
        "🔔 *НОВЫЙ ЗАКАЗ*\n\n"
        f"📦 Номер: `{order_data['order_number']}`\n"
        f"👤 Клиент: {order_data['username']}\n"
        f"📱 Телефон: `{order_data['phone']}`\n"
        f"📍 Адрес: {order_data['address']}\n\n"
        f"🍣 *Товары:*\n{items_text}\n"
        f"💰 *Сумма:* {order_data['total_price']}₽\n"
        f"💳 *Оплата:* {order_data['payment_method']}\n"
    )

    if order_data.get("comment"):
        message_text += f"📝 *Комментарий:* {order_data['comment']}\n"

    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=message_text,
            message_thread_id=ORDERS_TOPIC_ID,
            parse_mode="Markdown",
        )
        logger.info(
            f"✅ Уведомление отправлено админу. Заказ #{order_data['order_number']}"
        )
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке уведомления: {e}")


async def notify_user_order_received(user_id: int, order_number: str):
    """Отправить клиенту подтверждение заказа"""

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🍣 Новый заказ", web_app=WebAppInfo(url=MINI_APP_URL)
                )
            ],
        ]
    )

    await bot.send_message(
        chat_id=user_id,
        text=(
            f"✅ *Спасибо за заказ!*\n\n"
            f"📦 Номер заказа: `{order_number}`\n"
            f"⏰ Время доставки: 45–60 минут\n\n"
            f"Мы уведомим тебя, когда заказ выйдет на доставку!"
        ),
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


# ============= WEBHOOK ДЛЯ ПОЛУЧЕНИЯ ЗАКАЗОВ =============


async def process_webhook_order(order_data: dict):
    """Обработка заказа из Mini App (вызывается из API)"""

    user_id = order_data["telegram_user_id"]

    # Уведомляем админа
    await notify_admin_about_order(order_data)

    # Уведомляем клиента
    await notify_user_order_received(user_id, order_data["order_number"])


# ============= ЗАПУСК БОТА =============


async def main():
    logger.info("🤖 Бот запущен...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
