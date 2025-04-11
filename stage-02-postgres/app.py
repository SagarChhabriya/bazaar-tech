from fastapi import FastAPI, HTTPException
import psycopg2
from fastapi.security import HTTPBasic

app = FastAPI()
security = HTTPBasic()

# PostgreSQL connection
conn = psycopg2.connect(
    dbname="inventory_db", 
    user="postgres",
    password="root",
    host="localhost"
)


@app.get("/")
def root():
    return {"message": "Inventory API is running "}


@app.post("/products")
def add_product(name: str):
    cur = conn.cursor()
    cur.execute("INSERT INTO products (name) VALUES (%s) RETURNING id", (name,))
    conn.commit()
    return {"id": cur.fetchone()[0]}


@app.post("/stores/{store_id}/stock")
def add_stock(store_id: int, product_id: int, qty: int):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO inventory (store_id, product_id, qty) 
        VALUES (%s, %s, %s)
        ON CONFLICT (store_id, product_id) 
        DO UPDATE SET qty = inventory.qty + %s
    """, (store_id, product_id, qty, qty))
    conn.commit()
    return {"status": "updated"}
