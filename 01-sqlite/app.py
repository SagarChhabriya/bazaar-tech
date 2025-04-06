import sqlite3
from dataclasses import dataclass

# Data Model 
@dataclass
class Product:
    id: int
    name: str
    current_stock: int


@dataclass
class StockMovement:
    product_id: int
    movement_type: str  # "IN", "SALE", "REMOVAL"
    quantity: int
    timestamp: str


# Database Setup
def init_db():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            current_stock INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_movements (
            product_id INTEGER,
            movement_type TEXT,
            quantity INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    conn.commit()
    conn.close()


# Inventory Operations
def add_stock(product_id: int, quantity: int):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET current_stock = current_stock + ? WHERE id = ?", (quantity, product_id))
    cursor.execute(
        "INSERT INTO stock_movements (product_id, movement_type, quantity) VALUES (?, 'IN', ?)", (product_id, quantity))
    conn.commit()
    conn.close()


def sell_product(product_id: int, quantity: int):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET current_stock = current_stock - ? WHERE id = ?", (quantity, product_id))
    cursor.execute(
        "INSERT INTO stock_movements (product_id, movement_type, quantity) VALUES (?, 'SALE', ?)", (product_id, quantity))
    conn.commit()
    conn.close()


# CLI Interface
if __name__ == "__main__":
    init_db()
    while True:
        print("\n1. Add Stock\n2. Sell Product\n3. Exit")
        choice = input("Choose action: ")
        if choice == "1":
            product_id = int(input("Product ID: "))
            quantity = int(input("Quantity: "))
            add_stock(product_id, quantity)
        elif choice == "2":
            product_id = int(input("Product ID: "))
            quantity = int(input("Quantity: "))
            sell_product(product_id, quantity)
        elif choice == "3":
            break
