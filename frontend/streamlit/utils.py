"""
Utility functions for the EDEKA Analytics Dashboard.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import traceback

# Add project root to Python path
sys.path.append('/Users/kunnath/Projects/EDEKA_Stepaniak')

# Try to import required modules, handle gracefully if missing
try:
    from src.utils.db_utils import get_internal_db_engine, get_db_session
except ImportError as e:
    st.error(f"Error importing database utilities: {e}")
    st.info("Make sure you're running this from the project root and all dependencies are installed.")

# Category mapping for better readability
CATEGORY_MAPPING = {
    1: 'Fresh Produce',
    2: 'Dairy',
    3: 'Bakery',
    4: 'Meat & Seafood',
    5: 'Frozen Foods',
    6: 'Beverages',
    7: 'Snacks',
    8: 'Household',
    9: 'Personal Care',
    10: 'Other'
}

@st.cache_data(ttl=600)
def get_data(query):
    """Execute a SQL query and return the results as a DataFrame."""
    engine = get_internal_db_engine()
    try:
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_sales_data(days=30):
    """Get sales data for the specified time period."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    query = f"""
    SELECT s.bill_id, s.purchase_date, s.quantity, s.unit_price, s.total_price,
           p.name as product_name, p.category_id,
           c.first_name, c.last_name,
           st.name as store_name, st.city
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    JOIN customers c ON s.customer_id = c.customer_id
    JOIN stores st ON s.store_id = st.store_id
    WHERE s.purchase_date BETWEEN '{start_date}' AND '{end_date}'
    """
    return get_data(query)

@st.cache_data(ttl=600)
def get_product_data():
    """Get product data."""
    query = """
    SELECT p.product_id, p.name, p.category_id, p.price, p.description
    FROM products p
    """
    return get_data(query)

@st.cache_data(ttl=600)
def get_customer_data():
    """Get customer data."""
    query = """
    SELECT c.customer_id, c.first_name, c.last_name, c.email, c.registration_date, c.last_purchase_date
    FROM customers c
    """
    return get_data(query)

@st.cache_data(ttl=600)
def get_store_data():
    """Get store data."""
    query = """
    SELECT s.store_id, s.name, s.city, s.postal_code
    FROM stores s
    """
    return get_data(query)

@st.cache_data(ttl=600)
def get_sales_summary():
    """Get sales summary data."""
    query = """
    SELECT 
        DATE(purchase_date) as date,
        SUM(total_price) as daily_sales,
        COUNT(DISTINCT bill_id) as num_transactions,
        SUM(quantity) as items_sold
    FROM sales
    GROUP BY DATE(purchase_date)
    ORDER BY date DESC
    LIMIT 30
    """
    return get_data(query)

@st.cache_data(ttl=600)
def get_top_products(limit=10):
    """Get top-selling products."""
    query = f"""
    SELECT 
        p.name as product_name,
        SUM(s.quantity) as units_sold,
        SUM(s.total_price) as total_revenue
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY p.product_id, p.name
    ORDER BY units_sold DESC
    LIMIT {limit}
    """
    return get_data(query)

@st.cache_data(ttl=600)
def get_category_sales():
    """Get sales by category."""
    query = """
    SELECT 
        p.category_id,
        SUM(s.total_price) as total_sales
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY p.category_id
    ORDER BY total_sales DESC
    """
    df = get_data(query)
    if not df.empty:
        df['category_name'] = df['category_id'].map(CATEGORY_MAPPING)
    return df

@st.cache_data(ttl=600)
def get_store_performance():
    """Get store performance data."""
    query = """
    SELECT 
        st.name as store_name,
        st.city,
        COUNT(DISTINCT s.bill_id) as num_transactions,
        SUM(s.total_price) as total_sales
    FROM sales s
    JOIN stores st ON s.store_id = st.store_id
    GROUP BY st.store_id, st.name, st.city
    ORDER BY total_sales DESC
    """
    return get_data(query)

@st.cache_data(ttl=600)
def get_customer_segments():
    """Get customer segments based on purchase behavior."""
    query = """
    SELECT 
        c.customer_id,
        c.first_name,
        c.last_name,
        COUNT(DISTINCT s.bill_id) as num_transactions,
        SUM(s.total_price) as total_spend,
        AVG(s.total_price) as avg_transaction_value,
        MAX(s.purchase_date) as last_purchase_date
    FROM customers c
    JOIN sales s ON c.customer_id = s.customer_id
    GROUP BY c.customer_id, c.first_name, c.last_name
    """
    df = get_data(query)
    if not df.empty:
        # Add RFM segments
        df['last_purchase_date'] = pd.to_datetime(df['last_purchase_date'])
        df['days_since_purchase'] = (datetime.now() - df['last_purchase_date']).dt.days
        
        # Segment customers
        df['recency_score'] = pd.qcut(df['days_since_purchase'], 3, labels=[3, 2, 1])
        df['frequency_score'] = pd.qcut(df['num_transactions'].rank(method='first'), 3, labels=[1, 2, 3])
        df['monetary_score'] = pd.qcut(df['total_spend'].rank(method='first'), 3, labels=[1, 2, 3])
        
        # Calculate RFM score
        df['rfm_score'] = df['recency_score'].astype(str) + df['frequency_score'].astype(str) + df['monetary_score'].astype(str)
        
        # Add segment labels
        segment_mapping = {
            '111': 'Lost Customer',
            '112': 'Lost Customer',
            '113': 'Lost High Value',
            '121': 'Lost Customer',
            '122': 'Lost Customer',
            '123': 'Lost High Value',
            '131': 'Lost High Value',
            '132': 'Lost High Value',
            '133': 'Lost High Value',
            '211': 'Low Value',
            '212': 'Low Value',
            '213': 'Medium Value',
            '221': 'Low Value',
            '222': 'Medium Value',
            '223': 'Medium Value',
            '231': 'Medium Value',
            '232': 'Medium Value',
            '233': 'High Value',
            '311': 'New Customer',
            '312': 'New Customer',
            '313': 'Promising',
            '321': 'Active',
            '322': 'Active',
            '323': 'Loyal',
            '331': 'Loyal',
            '332': 'Loyal',
            '333': 'Champion'
        }
        df['segment'] = df['rfm_score'].map(segment_mapping)
    
    return df

@st.cache_data(ttl=600)
def get_customer_data():
    """Get customer data."""
    query = """
    SELECT c.customer_id, c.first_name, c.last_name, c.email, c.registration_date, c.last_purchase_date
    FROM customers c
    """
    return get_data(query)

@st.cache_data(ttl=600)
def get_store_data():
    """Get store data."""
    query = """
    SELECT s.store_id, s.name, s.city, s.postal_code
    FROM stores s
    """
    return get_data(query)

@st.cache_data(ttl=600)
def get_sales_summary():
    """Get sales summary data."""
    query = """
    SELECT 
        DATE(purchase_date) as date,
        SUM(total_price) as daily_sales,
        COUNT(DISTINCT bill_id) as num_transactions,
        SUM(quantity) as items_sold
    FROM sales
    GROUP BY DATE(purchase_date)
    ORDER BY date DESC
    LIMIT 30
    """
    return get_data(query)

@st.cache_data(ttl=600)
def get_top_products(limit=10):
    """Get top-selling products."""
    query = f"""
    SELECT 
        p.name as product_name,
        SUM(s.quantity) as units_sold,
        SUM(s.total_price) as total_revenue
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY p.product_id, p.name
    ORDER BY units_sold DESC
    LIMIT {limit}
    """
    return get_data(query)

@st.cache_data(ttl=600)
def get_category_sales():
    """Get sales by category."""
    query = """
    SELECT 
        p.category_id,
        SUM(s.total_price) as total_sales
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY p.category_id
    ORDER BY total_sales DESC
    """
    return get_data(query)

@st.cache_data(ttl=600)
def get_store_performance():
    """Get store performance data."""
    query = """
    SELECT 
        st.name as store_name,
        st.city,
        COUNT(DISTINCT s.bill_id) as num_transactions,
        SUM(s.total_price) as total_sales
    FROM sales s
    JOIN stores st ON s.store_id = st.store_id
    GROUP BY st.store_id, st.name, st.city
    ORDER BY total_sales DESC
    """
    return get_data(query)

# Category mapping
CATEGORY_MAPPING = {
    1: "Produce",
    2: "Dairy",
    3: "Meat",
    4: "Bakery",
    5: "Frozen",
    6: "Beverages",
    7: "Snacks",
    8: "Household",
    9: "Health & Beauty",
    10: "Other"
}
