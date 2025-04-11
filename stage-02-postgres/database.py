# CREATE DATABASE inventory_db;
# CREATE USER inventory_user WITH PASSWORD 'root';
# GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;

# database.py
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:root@localhost/inventory_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (
        CheckConstraint("current_stock >= 0", name="stock_non_negative"),
    )

    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.id"), primary_key=True)
    current_stock = Column(Integer, default=0)


class Movement(Base):
    __tablename__ = "movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    store_id = Column(Integer, ForeignKey("stores.id"))
    type = Column(String, nullable=False)  # STOCK_IN, SALE, REMOVAL, TRANSFER
    quantity = Column(Integer, nullable=False)
    notes = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


# Create all tables
Base.metadata.create_all(bind=engine)
