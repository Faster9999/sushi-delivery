import sqlite3
import json

DB_PATH = "sushi.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Создаём таблицы
    c.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    c.execute("""
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
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_user_id INTEGER,
            username TEXT,
            phone TEXT,
            address TEXT,
            items TEXT,
            total_price REAL,
            comment TEXT,
            payment_method TEXT DEFAULT 'cash',
            order_number TEXT UNIQUE,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    
    # Добавляем категории
    categories = [
        ("Роллы", "rolls"),
        ("Суши", "sushi"),
        ("Напитки", "drinks"),
    ]
    
    for name, slug in categories:
        try:
            c.execute("INSERT INTO categories (name, slug) VALUES (?, ?)", (name, slug))
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    
    # Добавляем суши (цена от 30000 до 55000 сум)
    sushi_products = [
        (1, "Филадельфия", "Классический ролл с лососем", "Лосось, сливочный сыр, огурец", 35000, "https://github.com/Faster9999/sushi-delivery/raw/main/img/s1.png", "🔥 Популярный"),
        (1, "Калифорния", "Ролл с крабом и авокадо", "Краб, авокадо, огурец, кунжут", 32000, "https://github.com/Faster9999/sushi-delivery/raw/main/img/s2.png", None),
        (2, "Нигири Лосось", "Кусочек лосося на рисе", "Лосось, рис", 30000, "https://github.com/Faster9999/sushi-delivery/raw/main/img/s3.png", None),
        (2, "Нигири Тунец", "Кусочек тунца на рисе", "Тунец, рис", 33000, "https://github.com/Faster9999/sushi-delivery/raw/main/img/s4.png", None),
        (1, "Унаги", "Ролл с угрём и соусом", "Угорь, соус унаги, кунжут", 40000, "https://github.com/Faster9999/sushi-delivery/raw/main/img/s5.png", "🌶️ Острый"),
        (1, "Дракон", "Красивый ролл с авокадо сверху", "Креветка, авокадо, сливочный сыр", 38000, "https://github.com/Faster9999/sushi-delivery/raw/main/img/s6.png", "⭐ Лучший"),
        (2, "Суши микс", "Ассортимент из 6 кусочков", "Лосось, тунец, креветка", 45000, "https://github.com/Faster9999/sushi-delivery/raw/main/img/s7.png", None),
        (1, "Спайси", "Острый ролл с кальмаром", "Кальмар, чили, кунжут", 34000, "https://github.com/Faster9999/sushi-delivery/raw/main/img/s8.png", "🔥 Острый"),
        (1, "Премиум", "Ролл с икрой и лососем", "Лосось, икра, сливочный сыр", 55000, "https://github.com/Faster9999/sushi-delivery/raw/main/img/s9.png", "👑 Премиум"),
        (1, "Веган", "Ролл с овощами", "Авокадо, огурец, морковь, кунжут", 28000, "https://github.com/Faster9999/sushi-delivery/raw/main/img/s10.png", "🌱 Веган"),
    ]
    
    for category_id, name, description, ingredients, price, image_url, badge in sushi_products:
        try:
            c.execute(
                "INSERT INTO products (category_id, name, description, ingredients, price, image_url, badge) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (category_id, name, description, ingredients, price, image_url, badge)
            )
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()
    
    print("✅ БД инициализирована")
    print("✅ Добавлены товары")

if __name__ == "__main__":
    init_db()