"""
Home page for EDEKA Analytics Dashboard.
"""
import streamlit as st
import pandas as pd
import os
import sys

# Add project root to Python path
sys.path.append('/Users/kunnath/Projects/EDEKA_Stepaniak')

# Try to import plotly, install if missing
try:
    import plotly.express as px
except ImportError:
    st.error("Plotly package is missing. Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])
    import plotly.express as px

try:
    from frontend.streamlit.utils import get_sales_summary, get_top_products, get_category_sales, CATEGORY_MAPPING, get_data
except ImportError as e:
    st.error(f"Error importing required modules: {e}")
    st.info("Make sure you have all required packages installed: pip install -r requirements.txt")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="EDEKA Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
st.sidebar.title("EDEKA Analytics")
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Edeka_Logo.svg/320px-Edeka_Logo.svg.png", width=200)

# Check if dev mode is enabled
dev_mode = os.getenv('EDEKA_DEV_MODE', 'false').lower() == 'true'
if dev_mode:
    st.sidebar.info("🔧 Development Mode: Using mock data")

# Main content
st.title("EDEKA Analytics Dashboard")
st.subheader("Real-time Retail Analytics & Insights")

# Introduction
st.markdown("""
This dashboard provides comprehensive analytics and insights for EDEKA retail operations.
Navigate through different views using the menu on the left to explore sales trends,
product performance, customer behavior, and store metrics.
""")

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
        
        # Create two columns for the charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Top products
            st.subheader("Top Selling Products")
            top_products = get_top_products(10)
            if not top_products.empty:
                fig = px.bar(
                    top_products,
                    x='product_name',
                    y='units_sold',
                    title="Top Products by Units Sold",
                    labels={"product_name": "Product", "units_sold": "Units Sold"}
                )
                fig.update_layout(xaxis={'categoryorder':'total descending'})
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Sales by category
            st.subheader("Sales by Category")
            category_sales = get_category_sales()
            if not category_sales.empty:
                # Map category IDs to names
                category_sales['category_name'] = category_sales['category_id'].map(CATEGORY_MAPPING)
                
                fig = px.pie(
                    category_sales,
                    values='total_sales',
                    names='category_name',
                    title="Sales Distribution by Category"
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No sales data available. Please make sure the database is properly initialized with mock data.")
except Exception as e:
    st.error(f"Error loading dashboard data: {e}")

# Quick navigation
st.subheader("Quick Navigation")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.info("📊 [Sales Analysis](/Sales_Analysis)")
    st.write("Analyze sales trends, patterns, and performance metrics.")

with col2:
    st.info("📦 [Product Insights](/Product_Insights)")
    st.write("Explore product performance, inventory, and category analysis.")

with col3:
    st.info("👥 [Customer Analytics](/Customer_Analytics)")
    st.write("Understand customer behavior, demographics, and purchase patterns.")

with col4:
    st.info("🏪 [Store Performance](/Store_Performance)")
    st.write("Compare store metrics, regional performance, and operational insights.")

# About section
with st.expander("About EDEKA Analytics Dashboard"):
    st.markdown("""
    ### EDEKA Analytics Dashboard
    
    This dashboard is designed to provide comprehensive analytics and insights for EDEKA retail operations.
    It integrates data from various sources to deliver actionable intelligence for business decision-making.
    
    **Key Features:**
    - Real-time sales monitoring and trend analysis
    - Product performance metrics and inventory insights
    - Customer behavior analysis and segmentation
    - Store performance comparison and operational metrics
    
    **Technologies Used:**
    - Python & Streamlit for the interactive dashboard
    - SQLAlchemy for database operations
    - Pandas for data manipulation
    - Plotly for interactive visualizations
    
    **Data Sources:**
    - EDEKA point-of-sale systems
    - Inventory management system
    - Customer relationship management (CRM) database
    - Store operations data
    """)

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
