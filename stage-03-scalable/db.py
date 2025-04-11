from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://user:pass@localhost/db", pool_size=20)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Inventory(Base):
    __tablename__ = 'inventory'
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    store_id = Column(Integer, ForeignKey('stores.id'), primary_key=True)
    current_stock = Column(Integer)

class StockMovement(Base):
    __tablename__ = 'stock_movements'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    store_id = Column(Integer)
    movement_type = Column(String(20))
    quantity = Column(Integer)
    timestamp = Column(DateTime, server_default='now()')

Base.metadata.create_all(bind=engine)