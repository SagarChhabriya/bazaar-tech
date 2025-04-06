import sqlite3
from datetime import datetime

# Initialize database with two tables


def init_db():
    conn = sqlite3.connect("inventory.sqlite")
    cursor = conn.cursor()

    # Products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        current_stock INTEGER DEFAULT 0
    )
    """)

    # Movements table (audit log)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        type TEXT CHECK(type IN ('STOCK_IN', 'SALE', 'ADJUSTMENT')),
        quantity INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """)
    conn.commit()
    conn.close()

# Add new product


def add_product(name):
    conn = sqlite3.connect("inventory.sqlite")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products (name) VALUES (?)", (name,))
        conn.commit()
        print(f"Added product: {name}")
    except sqlite3.IntegrityError:
        print(f"Product '{name}' already exists!")
    finally:
        conn.close()

# Record movement and update stock


def record_movement(product_id, movement_type, quantity):
    conn = sqlite3.connect("inventory.sqlite")
    cursor = conn.cursor()

    try:
        # Record the movement
        cursor.execute("""
        INSERT INTO movements (product_id, type, quantity)
        VALUES (?, ?, ?)
        """, (product_id, movement_type, quantity))

        # Update current stock
        if movement_type == 'STOCK_IN':
            cursor.execute("""
            UPDATE products 
            SET current_stock = current_stock + ? 
            WHERE id = ?
            """, (quantity, product_id))
        else:  # SALE or ADJUSTMENT
            cursor.execute("""
            UPDATE products 
            SET current_stock = current_stock - ? 
            WHERE id = ?
            """, (quantity, product_id))

        conn.commit()
        print(f"Recorded {movement_type} of {quantity} units")

    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()

# View current inventory


def view_inventory():
    conn = sqlite3.connect("inventory.sqlite")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, current_stock 
    FROM products
    ORDER BY name
    """)

    print("\nCurrent Inventory:")
    print(f"{'ID':<5}{'Product':<20}{'Stock':<10}")
    print("-" * 35)
    for row in cursor.fetchall():
        print(f"{row[0]:<5}{row[1]:<20}{row[2]:<10}")
    conn.close()

# View movement history


def view_movements(product_id=None):
    conn = sqlite3.connect("inventory.sqlite")
    cursor = conn.cursor()

    if product_id:
        cursor.execute("""
        SELECT m.type, m.quantity, m.timestamp, p.name
        FROM movements m
        JOIN products p ON m.product_id = p.id
        WHERE m.product_id = ?
        ORDER BY m.timestamp DESC
        LIMIT 10
        """, (product_id,))
        title = f"Last 10 movements for product {product_id}"
    else:
        cursor.execute("""
        SELECT m.type, m.quantity, m.timestamp, p.name
        FROM movements m
        JOIN products p ON m.product_id = p.id
        ORDER BY m.timestamp DESC
        LIMIT 10
        """)
        title = "Last 10 movements across all products"

    print(f"\n{title}:")
    print(f"{'Type':<10}{'Qty':<5}{'Product':<15}{'Time':<20}")
    print("-" * 50)
    for row in cursor.fetchall():
        print(f"{row[0]:<10}{row[1]:<5}{row[3]:<15}{row[2]:<20}")
    conn.close()


def delete_product(product_id):
    conn = sqlite3.connect("inventory.sqlite")
    cursor = conn.cursor()
    try:
        # Verify product exists
        cursor.execute("SELECT name FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        if not product:
            print("Error: Product not found!")
            return

        # Confirm deletion
        confirm = input(
            f"Delete {product[0]} (ID: {product_id})? This will remove ALL records! (y/n): ")
        if confirm.lower() != 'y':
            print("Cancelled")
            return

        # Delete the product and all its movements
        cursor.execute(
            "DELETE FROM movements WHERE product_id = ?", (product_id,))
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        print(f"Deleted product {product_id} and all related records")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


# Simple CLI Menu
def main():
    init_db()
    while True:
        print("\nINVENTORY SYSTEM")
        print("1. Add Product")
        print("2. Stock In")
        print("3. Record Sale")
        print("4. View Inventory")
        print("5. View Movements")
        print("6. Delete Product (Permanent Removal)")
        print("7. Exit")

        choice = input("Choose option (1-7): ")

        if choice == "1":
            name = input("Product name: ")
            add_product(name)

        elif choice == "2":
            view_inventory()
            pid = int(input("Product ID: "))
            qty = int(input("Quantity to add: "))
            record_movement(pid, 'STOCK_IN', qty)

        elif choice == "3":
            view_inventory()
            pid = int(input("Product ID: "))
            qty = int(input("Quantity sold: "))
            record_movement(pid, 'SALE', qty)

        elif choice == "4":
            view_inventory()

        elif choice == "5":
            view_inventory()
            pid = input("Product ID (press enter for all): ")
            view_movements(int(pid) if pid else None)

        elif choice == "6":
            view_inventory()
            pid = int(input("Product ID to delete: "))
            delete_product(pid)

        elif choice == "7":
            print("Exiting...")
            break

        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
