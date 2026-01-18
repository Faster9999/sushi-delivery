import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path("sushi.db")

def init_db():
    """Инициализация БД"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Категории
    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Товары
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            ingredients TEXT,
            price REAL NOT NULL,
            image_url TEXT,
            badge TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')
    
    # Заказы
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_user_id INTEGER NOT NULL,
            username TEXT,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            items TEXT NOT NULL,
            comment TEXT,
            total_price REAL NOT NULL,
            payment_method TEXT DEFAULT 'cash',
            status TEXT DEFAULT 'pending',
            order_number TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ БД инициализирована")

def seed_db():
    """Добавление тестовых данных"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    categories = [
        ("Сеты", "sets"),
        ("Роллы", "rolls"),
        ("Запечённые роллы", "hot-rolls"),
        ("Напитки", "drinks"),
        ("Соусы", "sauces"),
    ]
    
    for name, slug in categories:
        try:
            c.execute("INSERT INTO categories (name, slug) VALUES (?, ?)", (name, slug))
        except sqlite3.IntegrityError:
            pass
    
    products = [
        (1, "Сет Премиум", "8 штук асортированных роллов", "Лосось, авокадо, огурец", 450, None, "HIT"),
        (2, "Филадельфия", "Сливочный сыр, лосось, авокадо", "Нори, рис, сливочный сыр, лосось, авокадо", 320, None, None),
        (2, "Калифорния", "Крабовое мясо, авокадо, огурец", "Нори, рис, крабовое мясо, авокадо, огурец", 290, None, "NEW"),
        (3, "Запечённая Филадельфия", "С сыром и кунжутом сверху", "Нори, рис, сливочный сыр, лосось, авокадо, кунжут", 380, None, None),
        (4, "Coca-Cola", "Объем 330мл", "Coca-Cola", 50, None, None),
        (4, "Вода", "Чистая питьевая вода 500мл", "Вода", 30, None, None),
        (5, "Соевый соус", "Порция 50мл", "Соевый соус", 15, None, None),
        (5, "Васаби", "Острый соус", "Васаби", 20, None, None),
    ]
    
    for cat_id, name, description, ingredients, price, image, badge in products:
        try:
            c.execute(
                "INSERT INTO products (category_id, name, description, ingredients, price, image_url, badge) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (cat_id, name, description, ingredients, price, image, badge)
            )
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()
    print("✅ Тестовые данные добавлены")

if __name__ == "__main__":
    init_db()
    seed_db()