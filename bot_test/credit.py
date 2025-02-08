from telegram import Update
from telegram.ext import ContextTypes
import math


def calculate_credit_payment(amount: float, rate: float, months: int) -> float:
    """Рассчитывает ежемесячный платеж по кредиту."""
    monthly_rate = rate / 100 / 12
    return amount * (monthly_rate * math.pow(1 + monthly_rate, months)) / (math.pow(1 + monthly_rate, months) - 1)


async def credit_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.strip()
        parts = text.split()
        if len(parts) != 3:
            raise ValueError(
                "Неверный формат данных. Введите сумму, процентную ставку и срок кредита в месяцах через пробел.")

        amount, rate, months = map(float, parts)
        if amount <= 0 or rate <= 0 or months <= 0:
            raise ValueError("Числа должны быть больше нуля.")

        payment = calculate_credit_payment(amount, rate, int(months))

        await update.message.reply_text(f"✅ Ежемесячный платеж: `{payment:.2f}` руб.", parse_mode="Markdown")
    except ValueError as e:
        await update.message.reply_text(f"⛔ Ошибка: {e}", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text("⛔ Внутренняя ошибка. Попробуйте еще раз.", parse_mode="Markdown")
