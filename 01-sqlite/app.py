import sqlite3
from dataclasses import dataclass
from datetime import datetime

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
    # Insert some sample products if empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO products (id, name, current_stock) VALUES (?, ?, ?)",
            [(1, "Apple", 50), (2, "Banana", 30), (3, "Orange", 20)]
        )
    conn.commit()
    conn.close()


# Inventory Operations
def add_stock(product_id: int, quantity: int):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET current_stock = current_stock + ? WHERE id = ?", 
        (quantity, product_id))
    cursor.execute(
        "INSERT INTO stock_movements (product_id, movement_type, quantity) VALUES (?, 'IN', ?)", 
        (product_id, quantity))
    conn.commit()
    conn.close()


def sell_product(product_id: int, quantity: int):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET current_stock = current_stock - ? WHERE id = ?", 
        (quantity, product_id))
    cursor.execute(
        "INSERT INTO stock_movements (product_id, movement_type, quantity) VALUES (?, 'SALE', ?)", 
        (product_id, quantity))
    conn.commit()
    conn.close()


def show_products():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, current_stock FROM products")
    products = cursor.fetchall()
    conn.close()
    
    print("\nCurrent Inventory:")
    print("{:<5} {:<20} {:<10}".format("ID", "Product Name", "Quantity"))
    print("-" * 40)
    for product in products:
        print("{:<5} {:<20} {:<10}".format(product[0], product[1], product[2]))


def show_movements(product_id: int):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT movement_type, quantity, timestamp 
        FROM stock_movements 
        WHERE product_id = ?
        ORDER BY timestamp DESC
        LIMIT 10
    """, (product_id,))
    movements = cursor.fetchall()
    conn.close()
    
    print(f"\nRecent movements for product {product_id}:")
    print("{:<10} {:<10} {:<20}".format("Type", "Quantity", "Timestamp"))
    print("-" * 40)
    for move in movements:
        print("{:<10} {:<10} {:<20}".format(move[0], move[1], move[2]))


# CLI Interface
def main_menu():
    print("\nInventory Management System")
    print("1. View Current Stock")
    print("2. Add Stock")
    print("3. Sell Product")
    print("4. View Product History")
    print("5. Exit")


if __name__ == "__main__":
    init_db()
    while True:
        main_menu()
        choice = input("Choose action (1-5): ")
        
        if choice == "1":
            show_products()
            
        elif choice == "2":
            show_products()
            product_id = int(input("Enter product ID to restock: "))
            quantity = int(input("Enter quantity to add: "))
            add_stock(product_id, quantity)
            print(f"Added {quantity} units to product {product_id}")
            
        elif choice == "3":
            show_products()
            product_id = int(input("Enter product ID to sell: "))
            quantity = int(input("Enter quantity to sell: "))
            sell_product(product_id, quantity)
            print(f"Sold {quantity} units of product {product_id}")
            
        elif choice == "4":
            show_products()
            product_id = int(input("Enter product ID to view history: "))
            show_movements(product_id)
            
        elif choice == "5":
            print("Exiting inventory system...")
            break
            
        else:
            print("Invalid choice. Please enter 1-5.")