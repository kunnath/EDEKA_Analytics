"""
Database models for the EDEKA analytics application.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Product(Base):
    """Product model representing items sold in stores."""
    __tablename__ = 'products'
    
    product_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    category_id = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    # Relationships
    sales = relationship("Sale", back_populates="product")
    
    def __repr__(self):
        return f"<Product(product_id={self.product_id}, name='{self.name}')>"


class Customer(Base):
    """Customer model representing shoppers."""
    __tablename__ = 'customers'
    
    customer_id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True, unique=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    registration_date = Column(DateTime, nullable=False)
    last_purchase_date = Column(DateTime, nullable=True)
    
    # Relationships
    sales = relationship("Sale", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer(customer_id={self.customer_id}, name='{self.first_name} {self.last_name}')>"


class Store(Base):
    """Store model representing EDEKA store locations."""
    __tablename__ = 'stores'
    
    store_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Relationships
    sales = relationship("Sale", back_populates="store")
    
    def __repr__(self):
        return f"<Store(store_id={self.store_id}, name='{self.name}')>"


class Sale(Base):
    """Sale model representing individual product sales."""
    __tablename__ = 'sales'
    
    sale_id = Column(Integer, primary_key=True)
    bill_id = Column(String(50), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'), nullable=False)
    store_id = Column(Integer, ForeignKey('stores.store_id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    purchase_date = Column(DateTime, nullable=False, index=True)
    
    # Relationships
    product = relationship("Product", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")
    store = relationship("Store", back_populates="sales")
    
    def __repr__(self):
        return f"<Sale(sale_id={self.sale_id}, bill_id='{self.bill_id}', product_id={self.product_id})>"


class SyncLog(Base):
    """SyncLog model for tracking data synchronization operations."""
    __tablename__ = 'sync_logs'
    
    log_id = Column(Integer, primary_key=True)
    sync_start = Column(DateTime, nullable=False)
    sync_end = Column(DateTime, nullable=True)
    table_name = Column(String(100), nullable=False)
    records_fetched = Column(Integer, nullable=False, default=0)
    records_inserted = Column(Integer, nullable=False, default=0)
    records_updated = Column(Integer, nullable=False, default=0)
    records_failed = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False)  # 'success', 'failed', 'in_progress'
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<SyncLog(log_id={self.log_id}, table='{self.table_name}', status='{self.status}')>"


def init_db(engine):
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(engine)
