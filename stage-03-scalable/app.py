from fastapi import FastAPI, Depends, HTTPException
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis
from db import SessionLocal, Product, Store, Inventory, StockMovement, get_db
from sqlalchemy.orm import Session
from celery import Celery
import json

app = FastAPI() 
redis_client = redis.Redis(host='localhost', port=6379, db=0)
celery = Celery('tasks', broker='redis://localhost:6379/0')

@app.on_event("startup")
async def startup():
    await FastAPILimiter.init(redis_client)

@celery.task
def async_log_movement(movement_data: dict):
    with SessionLocal() as db:
        db.add(StockMovement(**movement_data))
        db.commit()

@app.post("/movements")
async def create_movement(
    product_id: int,
    store_id: int,
    movement_type: str,
    quantity: int,
    db: Session = Depends(get_db),
    _: str = Depends(RateLimiter(times=30, minutes=1))
):
    # Validate and update inventory
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id,
        Inventory.store_id == store_id
    ).with_for_update().first()
    
    if movement_type in ['SALE', 'REMOVAL'] and (not inventory or inventory.current_stock < quantity):
        raise HTTPException(400, "Insufficient stock")
    
    # Async processing
    movement_data = {
        "product_id": product_id,
        "store_id": store_id,
        "movement_type": movement_type,
        "quantity": quantity
    }
    async_log_movement.delay(movement_data)
    
    # Update cache
    redis_client.delete(f"inventory:{store_id}")
    
    return {"status": "processing"}

@app.get("/inventory/{store_id}")
async def get_inventory(store_id: int):
    # Check cache first
    cached = redis_client.get(f"inventory:{store_id}")
    if cached:
        return {"source": "cache", "data": json.loads(cached)}
    
    # Fallback to DB
    with SessionLocal() as db:
        inventory = db.query(Inventory).filter(Inventory.store_id == store_id).all()
        data = [{"product_id": i.product_id, "stock": i.current_stock} for i in inventory]
        redis_client.setex(f"inventory:{store_id}", 30, json.dumps(data))
        return {"source": "db", "data": data}