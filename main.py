from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import json
import os
from dotenv import load_dotenv
import random
import string

load_dotenv()

app = FastAPI(title="TokyoGo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "sushi.db"


class Category(BaseModel):
    id: int
    name: str
    slug: str


class Product(BaseModel):
    id: int
    category_id: int
    name: str
    description: str
    ingredients: str
    price: float
    image_url: str | None
    badge: str | None


class OrderItem(BaseModel):
    product_id: int
    quantity: int
    name: str
    price: float


class OrderRequest(BaseModel):
    telegram_user_id: int
    username: str
    phone: str
    address: str
    items: list[OrderItem]
    total_price: float
    comment: str | None = None
    payment_method: str = "cash"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def dict_from_row(row):
    return dict(row) if row else None


@app.get("/")
async def root():
    return {"status": "ok", "app": "TokyoGo"}


@app.get("/mini-app", response_class=HTMLResponse)
async def serve_mini_app():
    try:
        with open("mini_app.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Mini App not found")


@app.get("/api/categories", response_model=list[Category])
async def get_categories():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, name, slug FROM categories ORDER BY id")
    categories = [dict_from_row(row) for row in c.fetchall()]
    conn.close()
    return categories


@app.get("/api/products", response_model=list[Product])
async def get_products(category_id: int = None):
    conn = get_db()
    c = conn.cursor()

    if category_id:
        c.execute(
            "SELECT id, category_id, name, description, ingredients, price, image_url, badge FROM products WHERE category_id = ? AND is_active = 1",
            (category_id,),
        )
    else:
        c.execute(
            "SELECT id, category_id, name, description, ingredients, price, image_url, badge FROM products WHERE is_active = 1"
        )

    products = [dict_from_row(row) for row in c.fetchall()]
    conn.close()
    return products


@app.get("/api/search")
async def search_products(q: str):
    conn = get_db()
    c = conn.cursor()
    query = f"%{q}%"
    c.execute(
        "SELECT id, category_id, name, description, ingredients, price, image_url, badge FROM products WHERE (name LIKE ? OR ingredients LIKE ?) AND is_active = 1",
        (query, query),
    )
    products = [dict_from_row(row) for row in c.fetchall()]
    conn.close()
    return products


@app.post("/api/orders")
async def create_order(order: OrderRequest):
    conn = get_db()
    c = conn.cursor()
    order_number = "".join(random.choices(string.digits, k=6))
    items_json = json.dumps([item.dict() for item in order.items])

    try:
        c.execute(
            """INSERT INTO orders 
            (telegram_user_id, username, phone, address, items, total_price, comment, payment_method, order_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                order.telegram_user_id,
                order.username,
                order.phone,
                order.address,
                items_json,
                order.total_price,
                order.comment,
                order.payment_method,
                order_number,
            ),
        )
        conn.commit()
        order_id = c.lastrowid
        conn.close()
        return {
            "success": True,
            "order_id": order_id,
            "order_number": order_number,
            "message": "Заказ принят!",
        }
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/orders/{order_id}")
async def get_order(order_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order = dict_from_row(c.fetchone())
    conn.close()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    order["items"] = json.loads(order["items"])
    return order


@app.get("/admin", response_class=HTMLResponse)
async def admin_panel():
    try:
        with open("admin.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Admin panel not found")


@app.get("/api/admin/orders")
async def get_orders():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 50")
    orders = [dict_from_row(row) for row in c.fetchall()]
    conn.close()
    for order in orders:
        order["items"] = json.loads(order["items"])
    return orders


@app.post("/api/admin/products")
async def create_product(product: Product):
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO products (category_id, name, description, ingredients, price, image_url, badge) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                product.category_id,
                product.name,
                product.description,
                product.ingredients,
                product.price,
                product.image_url,
                product.badge,
            ),
        )
        conn.commit()
        product_id = c.lastrowid
        conn.close()
        return {"success": True, "product_id": product_id}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/admin/products/{product_id}")
async def delete_product(product_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE products SET is_active=0 WHERE id=?", (product_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Товар удалён"}


@app.put("/api/admin/orders/{order_id}/status")
async def update_order_status(order_id: int, status: str):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"Статус обновлён на {status}"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
