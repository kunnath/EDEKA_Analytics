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
    SELECT s.bill_id, s.customer_id, s.purchase_date, s.quantity, s.unit_price, s.total_price,
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
    try:
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
        LEFT JOIN sales s ON c.customer_id = s.customer_id
        GROUP BY c.customer_id, c.first_name, c.last_name
        """
        df = get_data(query)
        
        if df.empty:
            return pd.DataFrame()
            
        # Replace NaN values with appropriate defaults
        df['num_transactions'] = df['num_transactions'].fillna(0)
        df['total_spend'] = df['total_spend'].fillna(0)
        df['avg_transaction_value'] = df['avg_transaction_value'].fillna(0)
        
        # For customers with no purchases, use registration date as last purchase
        customer_data = get_customer_data()
        if not customer_data.empty:
            # Create a mapping of customer_id to registration_date
            customer_reg_dates = dict(zip(customer_data['customer_id'], pd.to_datetime(customer_data['registration_date'])))
            
            # Fill missing last_purchase_date with registration_date
            for idx, row in df.iterrows():
                if pd.isna(row['last_purchase_date']) and row['customer_id'] in customer_reg_dates:
                    df.at[idx, 'last_purchase_date'] = customer_reg_dates[row['customer_id']]
        
        # Convert to datetime after handling missing values
        df['last_purchase_date'] = pd.to_datetime(df['last_purchase_date'])
        
        # Fill any remaining NaNs with a default old date
        default_date = datetime.now() - timedelta(days=365)  # Default to 1 year ago
        df['last_purchase_date'] = df['last_purchase_date'].fillna(default_date)
        
        # Calculate days since purchase
        df['days_since_purchase'] = (datetime.now() - df['last_purchase_date']).dt.days
        
        # Segment customers - using try/except to handle any quantile errors
        try:
            # Handle the case where there might not be enough data for 3 quantiles
            if len(df) >= 3:
                # For recency, lower is better (more recent)
                recency_bins = [0, 30, 90, df['days_since_purchase'].max()]
                recency_labels = [3, 2, 1]
                df['recency_score'] = pd.cut(df['days_since_purchase'], bins=recency_bins, labels=recency_labels, include_lowest=True)
                
                # For frequency and monetary, higher is better
                if df['num_transactions'].nunique() >= 3:
                    df['frequency_score'] = pd.qcut(df['num_transactions'].rank(method='first'), 3, labels=[1, 2, 3])
                else:
                    df['frequency_score'] = df['num_transactions'].apply(lambda x: 3 if x >= 5 else (2 if x >= 2 else 1))
                    
                if df['total_spend'].nunique() >= 3:
                    df['monetary_score'] = pd.qcut(df['total_spend'].rank(method='first'), 3, labels=[1, 2, 3])
                else:
                    df['monetary_score'] = df['total_spend'].apply(lambda x: 3 if x >= 500 else (2 if x >= 100 else 1))
            else:
                # Not enough data for quantiles, use simple scoring
                df['recency_score'] = df['days_since_purchase'].apply(lambda x: 3 if x <= 30 else (2 if x <= 90 else 1))
                df['frequency_score'] = df['num_transactions'].apply(lambda x: 3 if x >= 5 else (2 if x >= 2 else 1))
                df['monetary_score'] = df['total_spend'].apply(lambda x: 3 if x >= 500 else (2 if x >= 100 else 1))
            
            # Convert to string to create the RFM score
            df['recency_score'] = df['recency_score'].astype(str)
            df['frequency_score'] = df['frequency_score'].astype(str)
            df['monetary_score'] = df['monetary_score'].astype(str)
            
            # Calculate RFM score
            df['rfm_score'] = df['recency_score'] + df['frequency_score'] + df['monetary_score']
            
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
            # Handle any missing mappings
            df['segment'] = df['segment'].fillna('Other')
            
        except Exception as e:
            print(f"Error during customer segmentation: {e}")
            # Provide a basic segmentation as fallback
            df['segment'] = 'Unsegmented'
        
        return df
    except Exception as e:
        print(f"Error in get_customer_segments: {e}")
        traceback.print_exc()  # Print full traceback for easier debugging
        return pd.DataFrame()

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
