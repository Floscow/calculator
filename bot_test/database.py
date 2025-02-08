import sqlite3

# Подключение к базе данных
conn = sqlite3.connect("bot_database.db")
cursor = conn.cursor()

# Создание таблицы пользователей
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        name TEXT NOT NULL
    )
''')

# Создание таблицы расчетов
cursor.execute('''
    CREATE TABLE IF NOT EXISTS calculations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL NOT NULL,
        rate REAL NOT NULL,
        days INTEGER NOT NULL,
        result REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

# Сохранение изменений и закрытие соединения
conn.commit()
conn.close()

# Функция для добавления пользователя
def add_user(telegram_id, name):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (telegram_id, name) VALUES (?, ?)", (telegram_id, name))
    conn.commit()
    conn.close()

# Функция для получения ID пользователя
def get_user_id(telegram_id):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

# Функция для сохранения расчета
def save_calculation(telegram_id, amount, rate, days, result):
    user_id = get_user_id(telegram_id)
    if user_id:
        conn = sqlite3.connect("bot_database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO calculations (user_id, amount, rate, days, result) VALUES (?, ?, ?, ?, ?)",
                       (user_id, amount, rate, days, result))
        conn.commit()
        conn.close()
