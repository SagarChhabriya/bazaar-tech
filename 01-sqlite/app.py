import sqlite3

# Initialize database


def init_db():
    conn = sqlite3.connect("simple_inventory.db")
    cursor = conn.cursor()

    # Single table for everything
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stock INTEGER DEFAULT 0,
        last_updated TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

# Add new product


def add_product(name, initial_stock=0):
    conn = sqlite3.connect("simple_inventory.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, stock) VALUES (?, ?)",
        (name, initial_stock)
    )
    conn.commit()
    conn.close()
    print(f"Added: {name} (Initial stock: {initial_stock})")

# Update stock


def update_stock(product_id, change):
    conn = sqlite3.connect("simple_inventory.db")
    cursor = conn.cursor()

    # Get current stock
    cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
    current = cursor.fetchone()[0]
    new_stock = current + change

    if new_stock < 0:
        print("Error: Stock cannot go negative!")
        return

    # Update stock
    cursor.execute(
        "UPDATE products SET stock = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ?",
        (new_stock, product_id)
    )
    conn.commit()
    conn.close()
    print(
        f"Updated: Product {product_id} | Change: {change:+} | New stock: {new_stock}")

# List all products


def list_products():
    conn = sqlite3.connect("simple_inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, stock, last_updated FROM products")

    print("\nCurrent Inventory:")
    print(f"{'ID':<5}{'Product':<20}{'Stock':<10}{'Last Updated':<20}")
    print("-" * 50)
    for row in cursor.fetchall():
        print(f"{row[0]:<5}{row[1]:<20}{row[2]:<10}{row[3]:<20}")
    conn.close()

# Simple CLI


def main():
    init_db()
    while True:
        print("\n1. Add Product\n2. Add Stock\n3. Sell Product\n4. View Inventory\n5. Exit")
        choice = input("Choose option: ")

        if choice == "1":
            name = input("Product name: ")
            stock = int(input("Initial stock: "))
            add_product(name, stock)

        elif choice == "2":
            list_products()
            pid = int(input("Product ID: "))
            qty = int(input("Quantity to add: "))
            update_stock(pid, qty)

        elif choice == "3":
            list_products()
            pid = int(input("Product ID: "))
            qty = int(input("Quantity to sell: "))
            update_stock(pid, -qty)

        elif choice == "4":
            list_products()

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
