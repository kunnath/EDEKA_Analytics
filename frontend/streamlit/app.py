"""
EDEKA Analytics Dashboard

A Streamlit application for visualizing EDEKA sales, products, and customer data.
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os
from datetime import datetime, timedelta
import sys

# Add the project root to the Python path to import project modules
sys.path.append('/Users/kunnath/Projects/EDEKA_Stepaniak')

from src.utils.db_utils import get_internal_db_engine, get_db_session

# Set page configuration
st.set_page_config(
    page_title="EDEKA Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper functions
def get_data(query):
    """Execute a SQL query and return the results as a DataFrame."""
    engine = get_internal_db_engine()
    try:
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return pd.DataFrame()

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

def get_product_data():
    """Get product data."""
    query = """
    SELECT p.product_id, p.name, p.category_id, p.price, p.description
    FROM products p
    """
    return get_data(query)

def get_customer_data():
    """Get customer data."""
    query = """
    SELECT c.customer_id, c.first_name, c.last_name, c.email, c.registration_date, c.last_purchase_date
    FROM customers c
    """
    return get_data(query)

def get_store_data():
    """Get store data."""
    query = """
    SELECT s.store_id, s.name, s.city, s.postal_code
    FROM stores s
    """
    return get_data(query)

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

# Sidebar
st.sidebar.title("EDEKA Analytics")
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Edeka_Logo.svg/320px-Edeka_Logo.svg.png", width=200)

# Navigation
page = st.sidebar.selectbox(
    "Select a Dashboard",
    ["Overview", "Sales Analysis", "Product Insights", "Customer Analytics", "Store Performance"]
)

# Time period filter
time_period = st.sidebar.slider(
    "Select Time Period (days)",
    min_value=7,
    max_value=365,
    value=30,
    step=7
)

# Check if dev mode is enabled to use mock data
dev_mode = os.getenv('EDEKA_DEV_MODE', 'false').lower() == 'true'
if dev_mode:
    st.sidebar.info("🔧 Development Mode: Using mock data")

# Main content
if page == "Overview":
    st.title("EDEKA Analytics Dashboard")
    st.subheader("Real-time Retail Analytics & Insights")
    
    # Summary cards
    try:
        sales_summary = get_sales_summary()
        
        if not sales_summary.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            total_sales = sales_summary['daily_sales'].sum()
            avg_daily_sales = sales_summary['daily_sales'].mean()
            total_transactions = sales_summary['num_transactions'].sum()
            total_items = sales_summary['items_sold'].sum()
            
            col1.metric("Total Sales", f"€{total_sales:,.2f}")
            col2.metric("Avg. Daily Sales", f"€{avg_daily_sales:,.2f}")
            col3.metric("Transactions", f"{total_transactions:,}")
            col4.metric("Items Sold", f"{total_items:,}")
            
            # Sales trend chart
            st.subheader("Sales Trend")
            fig = px.line(
                sales_summary.sort_values('date'), 
                x='date', 
                y='daily_sales',
                title="Daily Sales Trend",
                labels={"daily_sales": "Sales (€)", "date": "Date"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Top products
            st.subheader("Top Selling Products")
            top_products = get_top_products()
            if not top_products.empty:
                fig = px.bar(
                    top_products,
                    x='product_name',
                    y='units_sold',
                    title="Top Products by Units Sold",
                    labels={"product_name": "Product", "units_sold": "Units Sold"}
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No sales data available for the selected period.")
    except Exception as e:
        st.error(f"Error loading overview data: {e}")

elif page == "Sales Analysis":
    st.title("Sales Analysis")
    
    try:
        # Get sales data
        sales_data = get_sales_data(time_period)
        
        if not sales_data.empty:
            # Sales by date
            st.subheader("Sales by Date")
            sales_by_date = sales_data.groupby(pd.Grouper(key='purchase_date', freq='D')).agg({
                'total_price': 'sum',
                'bill_id': 'nunique',
                'quantity': 'sum'
            }).reset_index()
            
            sales_by_date.columns = ['Date', 'Total Sales', 'Transactions', 'Units Sold']
            
            # Create tabs for different visualizations
            tab1, tab2 = st.tabs(["Sales Trend", "Transaction Analysis"])
            
            with tab1:
                fig = px.line(
                    sales_by_date,
                    x='Date',
                    y='Total Sales',
                    title="Daily Sales Trend",
                    labels={"Total Sales": "Sales (€)"}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                fig = px.bar(
                    sales_by_date,
                    x='Date',
                    y=['Transactions', 'Units Sold'],
                    title="Transactions and Units Sold",
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Sales by hour
            st.subheader("Sales by Hour")
            sales_data['hour'] = sales_data['purchase_date'].dt.hour
            sales_by_hour = sales_data.groupby('hour').agg({
                'total_price': 'sum',
                'bill_id': 'nunique'
            }).reset_index()
            
            fig = px.line(
                sales_by_hour,
                x='hour',
                y='total_price',
                title="Sales by Hour of Day",
                labels={"hour": "Hour", "total_price": "Sales (€)"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Sales by store and city
            st.subheader("Sales by Location")
            sales_by_store = sales_data.groupby(['store_name', 'city']).agg({
                'total_price': 'sum',
                'bill_id': 'nunique'
            }).reset_index()
            
            fig = px.bar(
                sales_by_store.sort_values('total_price', ascending=False),
                x='store_name',
                y='total_price',
                color='city',
                title="Sales by Store and City",
                labels={"store_name": "Store", "total_price": "Sales (€)", "city": "City"}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No sales data available for the selected period.")
    except Exception as e:
        st.error(f"Error loading sales analysis data: {e}")

elif page == "Product Insights":
    st.title("Product Insights")
    
    try:
        # Get product data
        product_data = get_product_data()
        
        if not product_data.empty:
            # Product categories
            st.subheader("Products by Category")
            products_by_category = product_data.groupby('category_id').size().reset_index(name='count')
            
            fig = px.pie(
                products_by_category,
                values='count',
                names='category_id',
                title="Product Distribution by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Price distribution
            st.subheader("Price Distribution")
            fig = px.histogram(
                product_data,
                x='price',
                nbins=20,
                title="Product Price Distribution",
                labels={"price": "Price (€)"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Top-selling products
            st.subheader("Top Selling Products")
            top_products = get_top_products(20)
            
            if not top_products.empty:
                fig = px.bar(
                    top_products.head(20),
                    x='product_name',
                    y=['units_sold', 'total_revenue'],
                    barmode='group',
                    title="Top Products by Units Sold and Revenue",
                    labels={
                        "product_name": "Product",
                        "units_sold": "Units Sold",
                        "total_revenue": "Revenue (€)"
                    }
                )
                fig.update_layout(xaxis={'categoryorder':'total descending'})
                st.plotly_chart(fig, use_container_width=True)
            
            # Product table
            st.subheader("Product Catalog")
            st.dataframe(product_data, use_container_width=True)
        else:
            st.warning("No product data available.")
    except Exception as e:
        st.error(f"Error loading product insights data: {e}")

elif page == "Customer Analytics":
    st.title("Customer Analytics")
    
    try:
        # Get customer data
        customer_data = get_customer_data()
        
        if not customer_data.empty:
            # Customer registration over time
            st.subheader("Customer Registrations Over Time")
            customer_data['registration_date'] = pd.to_datetime(customer_data['registration_date'])
            customer_data['registration_month'] = customer_data['registration_date'].dt.to_period('M')
            
            registrations_by_month = customer_data.groupby('registration_month').size().reset_index(name='count')
            registrations_by_month['registration_month'] = registrations_by_month['registration_month'].astype(str)
            
            fig = px.line(
                registrations_by_month,
                x='registration_month',
                y='count',
                title="Customer Registrations by Month",
                labels={"registration_month": "Month", "count": "New Customers"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Customer retention analysis
            st.subheader("Customer Retention Analysis")
            customer_data['days_since_last_purchase'] = (
                datetime.now() - pd.to_datetime(customer_data['last_purchase_date'])
            ).dt.days
            
            retention_groups = [
                (0, 30, 'Active (0-30 days)'),
                (31, 90, 'Recent (31-90 days)'),
                (91, 180, 'Lapsed (91-180 days)'),
                (181, 365, 'Inactive (181-365 days)'),
                (366, float('inf'), 'Lost (366+ days)')
            ]
            
            customer_data['retention_group'] = None
            for min_days, max_days, group_name in retention_groups:
                mask = (customer_data['days_since_last_purchase'] >= min_days) & (customer_data['days_since_last_purchase'] <= max_days)
                customer_data.loc[mask, 'retention_group'] = group_name
            
            retention_counts = customer_data.groupby('retention_group').size().reset_index(name='count')
            
            fig = px.pie(
                retention_counts,
                values='count',
                names='retention_group',
                title="Customer Retention Analysis",
                color_discrete_sequence=px.colors.sequential.RdBu_r
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Customer table (sample)
            st.subheader("Customer Sample Data")
            st.dataframe(customer_data.head(100), use_container_width=True)
        else:
            st.warning("No customer data available.")
    except Exception as e:
        st.error(f"Error loading customer analytics data: {e}")

elif page == "Store Performance":
    st.title("Store Performance")
    
    try:
        # Get store performance data
        store_performance = get_store_performance()
        
        if not store_performance.empty:
            # Store sales comparison
            st.subheader("Store Sales Comparison")
            fig = px.bar(
                store_performance.sort_values('total_sales', ascending=False),
                x='store_name',
                y='total_sales',
                color='city',
                title="Total Sales by Store",
                labels={"store_name": "Store", "total_sales": "Sales (€)", "city": "City"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Transaction volume
            st.subheader("Transaction Volume by Store")
            fig = px.bar(
                store_performance.sort_values('num_transactions', ascending=False),
                x='store_name',
                y='num_transactions',
                color='city',
                title="Number of Transactions by Store",
                labels={"store_name": "Store", "num_transactions": "Transactions", "city": "City"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Average transaction value
            store_performance['avg_transaction_value'] = store_performance['total_sales'] / store_performance['num_transactions']
            
            st.subheader("Average Transaction Value")
            fig = px.bar(
                store_performance.sort_values('avg_transaction_value', ascending=False),
                x='store_name',
                y='avg_transaction_value',
                color='city',
                title="Average Transaction Value by Store",
                labels={"store_name": "Store", "avg_transaction_value": "Avg. Transaction (€)", "city": "City"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Store performance table
            st.subheader("Store Performance Data")
            st.dataframe(store_performance, use_container_width=True)
        else:
            st.warning("No store performance data available.")
    except Exception as e:
        st.error(f"Error loading store performance data: {e}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center">
        <p>EDEKA Analytics Dashboard | © 2025 EDEKA Group</p>
    </div>
    """,
    unsafe_allow_html=True
)
