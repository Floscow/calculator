from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton

# 📌 Главное меню
startMenu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='📋 Профиль'),
            KeyboardButton(text='💠 VPN')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder='Выберите действие'
)

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton

# 📌 Подменю VPN (обычные кнопки)
vpnMenu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='📥 Скачать конфиг'),
            KeyboardButton(text='💳 Купить VPN')
        ],
        [
            KeyboardButton(text='🔄 Проверить подписку'),
            KeyboardButton(text='🔙 Назад')
        ]
    ],
    resize_keyboard=True
)

# 📌 Инлайн-кнопки для покупки VPN (например, через сайт)
buyVpnInline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='🌐 Купить VPN', url='https://example.com/buy-vpn')
        ]
    ]
)
