"""
Utility script to initialize data for the EDEKA analytics dashboard.
"""
import os
import sys
import pandas as pd
from sqlalchemy import text
from datetime import datetime

# Add the project root to the Python path
sys.path.append('/Users/kunnath/Projects/EDEKA_Stepaniak')

from src.utils.db_utils import get_internal_db_engine, get_db_session
from src.utils.mock_data import get_mock_stores_data, get_mock_products_data, get_mock_customers_data, get_mock_sales_data
from src.utils.logger import logger

def initialize_store_data():
    """Initialize store data in the database if not already present."""
    # Set development mode
    os.environ['EDEKA_DEV_MODE'] = 'true'
    
    logger.info("Checking if store data needs to be initialized...")
    
    engine = get_internal_db_engine()
    
    with get_db_session(engine) as session:
        # Check if stores table has data
        result = session.execute(text("SELECT COUNT(*) FROM stores"))
        count = result.scalar()
        
        if count == 0:
            logger.info("No store data found. Initializing with mock data...")
            
            # Generate mock store data
            store_df = get_mock_stores_data(20)
            
            # Insert mock data
            for _, row in store_df.iterrows():
                record = row.to_dict()
                
                columns = ", ".join(record.keys())
                placeholders = ", ".join([f":{col}" for col in record.keys()])
                
                insert_query = text(f"INSERT INTO stores ({columns}) VALUES ({placeholders})")
                session.execute(insert_query, record)
            
            session.commit()
            logger.info(f"Successfully initialized {len(store_df)} store records")
            return len(store_df)
        else:
            logger.info(f"Store data already exists ({count} records). Skipping initialization.")
            return count

def initialize_product_data():
    """Initialize product data in the database if not already present."""
    logger.info("Checking if product data needs to be initialized...")
    
    engine = get_internal_db_engine()
    
    with get_db_session(engine) as session:
        # Check if products table has data
        result = session.execute(text("SELECT COUNT(*) FROM products"))
        count = result.scalar()
        
        if count == 0:
            logger.info("No product data found. Initializing with mock data...")
            
            # Generate mock product data
            product_df = get_mock_products_data(50)
            
            # Insert mock data
            for _, row in product_df.iterrows():
                record = row.to_dict()
                
                columns = ", ".join(record.keys())
                placeholders = ", ".join([f":{col}" for col in record.keys()])
                
                insert_query = text(f"INSERT INTO products ({columns}) VALUES ({placeholders})")
                session.execute(insert_query, record)
            
            session.commit()
            logger.info(f"Successfully initialized {len(product_df)} product records")
            return len(product_df)
        else:
            logger.info(f"Product data already exists ({count} records). Skipping initialization.")
            return count

def initialize_customer_data():
    """Initialize customer data in the database if not already present."""
    logger.info("Checking if customer data needs to be initialized...")
    
    engine = get_internal_db_engine()
    
    with get_db_session(engine) as session:
        # Check if customers table has data
        result = session.execute(text("SELECT COUNT(*) FROM customers"))
        count = result.scalar()
        
        if count == 0:
            logger.info("No customer data found. Initializing with mock data...")
            
            # Generate mock customer data
            customer_df = get_mock_customers_data(100)
            
            # Insert mock data
            for _, row in customer_df.iterrows():
                record = row.to_dict()
                
                columns = ", ".join(record.keys())
                placeholders = ", ".join([f":{col}" for col in record.keys()])
                
                insert_query = text(f"INSERT INTO customers ({columns}) VALUES ({placeholders})")
                session.execute(insert_query, record)
            
            session.commit()
            logger.info(f"Successfully initialized {len(customer_df)} customer records")
            return len(customer_df)
        else:
            logger.info(f"Customer data already exists ({count} records). Skipping initialization.")
            return count

def initialize_sales_data():
    """Initialize sales data in the database if not already present."""
    logger.info("Checking if sales data needs to be initialized...")
    
    engine = get_internal_db_engine()
    
    with get_db_session(engine) as session:
        # Check if sales table has data
        result = session.execute(text("SELECT COUNT(*) FROM sales"))
        count = result.scalar()
        
        if count == 0:
            logger.info("No sales data found. Initializing with mock data...")
            
            # Generate mock sales data
            sales_df = get_mock_sales_data(500)
            
            # Insert mock data
            for _, row in sales_df.iterrows():
                record = row.to_dict()
                
                columns = ", ".join(record.keys())
                placeholders = ", ".join([f":{col}" for col in record.keys()])
                
                insert_query = text(f"INSERT INTO sales ({columns}) VALUES ({placeholders})")
                session.execute(insert_query, record)
            
            session.commit()
            logger.info(f"Successfully initialized {len(sales_df)} sales records")
            return len(sales_df)
        else:
            logger.info(f"Sales data already exists ({count} records). Skipping initialization.")
            return count

def initialize_all_data():
    """Initialize all required data for the dashboard."""
    os.environ['EDEKA_DEV_MODE'] = 'true'
    
    # Initialize in the correct order to satisfy foreign key constraints
    logger.info("Starting data initialization process...")
    stores_count = initialize_store_data()
    products_count = initialize_product_data()
    customers_count = initialize_customer_data()
    sales_count = initialize_sales_data()
    
    logger.info(f"Data initialization complete: {stores_count} stores, {products_count} products, {customers_count} customers, {sales_count} sales records")

if __name__ == "__main__":
    initialize_all_data()
