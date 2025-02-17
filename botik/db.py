import sqlite3

class Database:
    def __init__(self, db_file):
        """Инициализация базы данных"""
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        """Создаёт таблицу пользователей, если её нет"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                referrer_id INTEGER,
                balance REAL DEFAULT 0.0
            )
        """)
        self.connection.commit()

    def user_exists(self, user_id):
        """Проверяет, существует ли пользователь (более быстрый запрос)"""
        result = self.cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return result is not None  # Возвращает True, если пользователь найден

    def add_user(self, user_id, referrer_id=None):
        """Добавляет пользователя в базу, если его нет"""
        if not self.user_exists(user_id):
            if referrer_id is not None:
                self.cursor.execute(
                    "INSERT INTO users (user_id, referrer_id, balance) VALUES (?, ?, ?)",
                    (user_id, referrer_id, 0.0)
                )
            else:
                self.cursor.execute(
                    "INSERT INTO users (user_id, balance) VALUES (?, ?)",
                    (user_id, 0.0)
                )
            self.connection.commit()  # Сохраняем изменения

    def get_balance(self, user_id):
        """Получает текущий баланс пользователя"""
        result = self.cursor.execute(
            "SELECT balance FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        return result[0] if result else 0.0  # Если запись не найдена, возвращаем 0.0

    def add_balance(self, user_id, amount):
        """Добавляет сумму к балансу пользователя"""
        if not self.user_exists(user_id):
            self.add_user(user_id)  # Если пользователя нет, создаём его
        self.cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        self.connection.commit()

    def count_referrals(self, user_id):
        """Считает количество рефералов пользователя"""
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE referrer_id = ?", (user_id,))
        result = self.cursor.fetchone()

        print(f"DEBUG: Запрос рефералов для {user_id}, результат: {result}")  # Для отладки

        return result[0] if result and result[0] else 0  # Если результат None, возвращаем 0

    def close(self):
        """Закрывает соединение с базой данных"""
        self.connection.close()
