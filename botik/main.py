import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties  # ✅ Добавляем это!
from db import Database
import config as cfg
import keyboards as kb

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание бота и базы данных
bot = Bot(token=cfg.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))  # ✅ Исправлено!
dp = Dispatcher()
db = Database('database.db')

# Проверяем ADMIN_USER_ID
ADMIN_USER_ID = getattr(cfg, "ADMIN_USER_ID", None)
if ADMIN_USER_ID is not None:
    ADMIN_USER_ID = int(ADMIN_USER_ID)
else:
    logging.warning("ADMIN_USER_ID не указан в config.py")

logging.info(f"ADMIN_USER_ID = {ADMIN_USER_ID}")


# 📌 Стартовое сообщение
@dp.message(CommandStart())
async def start(message: Message):
    if message.chat.type == 'private':
        if not db.user_exists(message.from_user.id):
            start_command = message.text
            referrer_id = start_command[7:] if len(start_command) > 7 else ""

            if referrer_id.isdigit():
                referrer_id = int(referrer_id)
                if referrer_id == message.from_user.id:
                    await message.answer("❌ Нельзя регистрироваться по собственной ссылке!")
                    return

                db.add_user(message.from_user.id, referrer_id)
                try:
                    await bot.send_message(referrer_id, "🔗 По вашей ссылке зарегистрировался новый пользователь!")
                except Exception as e:
                    logging.error(f"Ошибка при отправке сообщения рефереру: {e}")
            else:
                db.add_user(message.from_user.id)

    await message.answer(f"👋 Добро пожаловать, {message.from_user.first_name}!", reply_markup=kb.startMenu)

# 📌 Профиль пользователя
@dp.message(F.text == '📋 Профиль')
async def profile(message: Message):
    if message.chat.type == 'private':
        user_balance = db.get_balance(message.from_user.id)
        referrals = db.count_referrals(message.from_user.id)
        await message.answer(
            f'🆔 Твой ID: {message.from_user.id}\n'
            f'🔑 Реферальная ссылка: https://t.me/{cfg.BOT_NICKNAME}?start={message.from_user.id}\n'
            f'👥 Кол-во рефералов: {referrals}\n'
            f'💰 Баланс: {user_balance} RUB'
        )

# 📌 Обработчик кнопки "Мой VPN"
@dp.message(F.text == "💠 VPN")
@dp.message(Command("vpn"))
async def my_vpn_handler(message: types.Message):
    """Обработчик кнопки 'Мой VPN'"""
    await message.answer(
        "🌐 Ваш VPN-кабинет\n"
        "🔹 Здесь вы можете управлять своим VPN-доступом.\n"
        "🔗 Ссылка на настройку: https://example.com/vpn\n\n"
        "Выберите действие:",
        reply_markup=kb.vpnMenu  # Показываем подменю VPN
    )

# 📌 Команда "Добавить баланс"
@dp.message(Command("add_balance"))
async def add_balance_command(message: Message):
    try:
        logging.info(f"Пользователь {message.from_user.id} пытается добавить баланс. ADMIN_USER_ID = {ADMIN_USER_ID}")

        if message.from_user.id != ADMIN_USER_ID:
            await message.answer("❌ У вас нет прав для выполнения этой команды.")
            return

        args = message.text.split()
        if len(args) != 3:
            await message.answer("❌ Используйте команду так: /add_balance ID СУММА")
            return

        user_id, amount = args[1], args[2]

        if not user_id.isdigit():
            await message.answer("❌ Неверный формат ID!")
            return
        user_id = int(user_id)

        if not amount.replace(".", "", 1).isdigit():
            await message.answer("❌ Неверный формат суммы!")
            return
        amount = float(amount)
        amount = int(amount) if amount.is_integer() else amount

        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше 0.")
            return

        if not db.user_exists(user_id):
            await message.answer(f"❌ Пользователь с ID {user_id} не найден.")
            return

        db.add_balance(user_id, amount)
        await message.answer(f"✅ Баланс пользователя {user_id} увеличен на {amount} RUB.")

    except Exception as e:
        logging.error(f"Ошибка при добавлении баланса: {e}")
        await message.answer(f"❌ Ошибка: {e}")

@dp.message(F.text == "📥 Скачать конфиг")
async def download_vpn_config(message: Message):
    """Отправляем пользователю конфигурацию VPN"""
    await message.answer("📥 Вот твой конфиг для IOS/Android: [Скачать](https://example.com/config)", parse_mode="Markdown")
    await message.answer("📥 Вот твой конфиг для PC: [Скачать](https://example.com/config)", parse_mode="Markdown")

@dp.message(F.text == "💳 Купить VPN")
async def buy_vpn(message: Message):
    """Отправляем пользователю ссылку на покупку VPN"""
    await message.answer("💳 Вы можете купить VPN по ссылке ниже:", reply_markup=kb.buyVpnInline)

@dp.message(F.text == "🔄 Проверить подписку")
async def check_vpn_status(message: Message):
    """Проверяем, есть ли у пользователя подписка на VPN"""
    user_id = message.from_user.id
    vpn_status = "🔴 Подписка не активна"  # Здесь можно сделать проверку через базу данных
    await message.answer(f"🔄 Статус подписки: {vpn_status}")

@dp.message(F.text == "🔙 Назад")
async def go_back(message: Message):
    """Возвращаем пользователя в главное меню"""
    await message.answer("🔙 Возвращаемся в главное меню.", reply_markup=kb.startMenu)

# 📌 Запуск бота
async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка в основном цикле бота: {e}")

if __name__ == '__main__':
    asyncio.run(main())
