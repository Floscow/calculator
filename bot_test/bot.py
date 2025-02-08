import logging
import re
from datetime import datetime
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
from database import add_user, save_calculation
from cbr_rates import get_interest_rates  # Функция загрузки ставок ЦБ РФ
from credit import calculate_credit_payment


# Логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Функция приветствия
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    add_user(user.id, user.first_name)
    keyboard = [[KeyboardButton("📊 Расчет задолженности"), KeyboardButton("📈 Расчет по вкладу")],
                [KeyboardButton("💰 Кредитный калькулятор")],
                [KeyboardButton("ℹ️ Помощь"), KeyboardButton("📜 Описание"), KeyboardButton("❌ Выйти")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"👋 *Привет, {user.first_name}!*\n"
        "📌 _Я финансовый калькулятор:_\n"
        "1️⃣ Нажмите кнопку Описание.\n"
        "2️⃣ Выберите нужный вид расчета.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


# Функция обработки сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.strip()
        logging.info(f"Получено сообщение: {text}")

        commands = {
            "📊 Расчет задолженности": "Введите сумму и количество дней через пробел. Например: `10000 30`",
            "📈 Расчет по вкладу": "Введите сумму и дату начала в формате: `5000 12-06-2010`",
            "💰 Кредитный калькулятор": "Введите сумму, процентную ставку и срок кредита (в месяцах) через пробел. Например: `50000 10 12`",
            "ℹ️ Помощь": "📌 _Формат ввода:_\n\n- `10000 30` (сумма и дни)\n- `10000 8 30` (сумма, ставка, дни)\n- `50000 10 12` (кредит: сумма, ставка %, срок мес.)\n- `5000 12-06-2010` (сумма и дата начала)",
            "📜 Описание": "📜 *Описание расчетов:*\n\n1️⃣ *Расчет задолженности* - по ставке годовых процентов.\n2️⃣ *Расчет по вкладу* - с учетом изменений ставки ЦБ.\n- `3️⃣ *Кредитный калькулятор* - расчет ежемесячного платежа по формуле аннуитетного кредита.",
            "❌ Выйти": "🔙 Главное меню. Введите `/start` для нового расчета."
        }

        if text in commands:
            await update.message.reply_text(commands[text], parse_mode="Markdown")
            return

        # Проверка формата "сумма ставка срок"
        if re.match(r"^\d+\s+\d+(\.\d+)?\s+\d+$", text):
            amount, rate, months = map(float, text.split())
            payment = calculate_credit_payment(amount, rate, int(months))
            await update.message.reply_text(f"✅ Ваш ежемесячный платеж: `{payment:.2f}` руб.", parse_mode="Markdown")
            return

        # Проверка формата "сумма дни"
        if re.match(r"^\d+\s+\d+$", text):
            amount, days = map(float, text.split())
            if amount <= 0 or days <= 0:
                raise ValueError("Числа должны быть больше нуля")
            rate = get_interest_rates(datetime.now())[-1][1]
            debt = (amount * rate * days) / (100 * 365)
            save_calculation(update.message.from_user.id, amount, rate, days, debt)
            await update.message.reply_text(f"✅ *Рассчитанная задолженность:* `{debt:.2f}` руб.", parse_mode="Markdown")
            return

        # Проверка формата "сумма дата"
        if re.match(r"^\d+\s+\d{2}-\d{2}-\d{4}$", text):
            amount, date_str = text.split()
            amount = float(amount)
            start_date = datetime.strptime(date_str, "%d-%m-%Y")
            interest_rates = get_interest_rates(start_date)
            if not interest_rates:
                raise ValueError("Не удалось загрузить ставки ЦБ РФ")
            current_date = datetime.now()
            debt, prev_date = amount, start_date
            for rate_date, rate in interest_rates:
                days = (rate_date - prev_date).days
                debt += (debt * rate * days) / (100 * 365)
                prev_date = rate_date
            debt += (debt * interest_rates[-1][1] * (current_date - prev_date).days) / (100 * 365)
            await update.message.reply_text(f"✅ Итоговая сумма с процентами: `{debt:.2f}` руб.", parse_mode="Markdown")
            return

        raise ValueError("Неверный формат данных")
    except ValueError as e:
        await update.message.reply_text(f"⛔ Ошибка: {e}. Попробуйте еще раз.", parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await update.message.reply_text("⛔ Внутренняя ошибка. Попробуйте еще раз.", parse_mode="Markdown")


# Основная функция запуска бота
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
