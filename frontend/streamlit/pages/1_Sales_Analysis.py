"""
Sales Analysis page for the EDEKA Analytics Dashboard.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sys

# Add project root to Python path
sys.path.append('/Users/kunnath/Projects/EDEKA_Stepaniak')

from frontend.streamlit.utils import get_data, get_sales_data

# Page configuration
st.set_page_config(
    page_title="EDEKA Sales Analysis",
    page_icon="📊",
    layout="wide"
)

# Sidebar
st.sidebar.title("EDEKA Sales Analysis")

# Time period filter
time_period = st.sidebar.slider(
    "Select Time Period (days)",
    min_value=7,
    max_value=365,
    value=30,
    step=7
)

# Date range filter
end_date = datetime.now()
start_date = end_date - timedelta(days=time_period)
date_range = st.sidebar.date_input(
    "Custom Date Range",
    [start_date.date(), end_date.date()],
    format="YYYY-MM-DD"
)

# Main content
st.title("Sales Analysis")
st.write("Analyze sales trends and patterns across different dimensions.")

try:
    # Get sales data
    sales_data = get_sales_data(time_period)
    
    if not sales_data.empty:
        # KPI metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_sales = sales_data['total_price'].sum()
        avg_transaction = sales_data.groupby('bill_id')['total_price'].sum().mean()
        total_transactions = sales_data['bill_id'].nunique()
        avg_items_per_transaction = sales_data.groupby('bill_id')['quantity'].sum().mean()
        
        col1.metric("Total Sales", f"€{total_sales:,.2f}")
        col2.metric("Avg. Transaction", f"€{avg_transaction:,.2f}")
        col3.metric("Transactions", f"{total_transactions:,}")
        col4.metric("Avg. Items/Transaction", f"{avg_items_per_transaction:.1f}")
        
        # Create tabs for different visualizations
        tab1, tab2, tab3 = st.tabs(["Sales Trends", "Product Analysis", "Store Analysis"])
        
        with tab1:
            st.subheader("Sales Trends")
            
            # Sales by date
            sales_by_date = sales_data.groupby(pd.Grouper(key='purchase_date', freq='D')).agg({
                'total_price': 'sum',
                'bill_id': 'nunique',
                'quantity': 'sum'
            }).reset_index()
            
            sales_by_date.columns = ['Date', 'Total Sales', 'Transactions', 'Units Sold']
            
            # Daily sales trend
            fig = px.line(
                sales_by_date,
                x='Date',
                y='Total Sales',
                title="Daily Sales Trend",
                labels={"Total Sales": "Sales (€)"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Day of week analysis
            sales_data['day_of_week'] = sales_data['purchase_date'].dt.day_name()
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            sales_by_dow = sales_data.groupby('day_of_week').agg({
                'total_price': 'sum',
                'bill_id': 'nunique'
            }).reset_index()
            
            sales_by_dow['day_of_week'] = pd.Categorical(sales_by_dow['day_of_week'], categories=day_order, ordered=True)
            sales_by_dow = sales_by_dow.sort_values('day_of_week')
            
            fig = px.bar(
                sales_by_dow,
                x='day_of_week',
                y='total_price',
                title="Sales by Day of Week",
                labels={"day_of_week": "Day", "total_price": "Sales (€)"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Hour of day analysis
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
            
        with tab2:
            st.subheader("Product Analysis")
            
            # Sales by product
            sales_by_product = sales_data.groupby('product_name').agg({
                'quantity': 'sum',
                'total_price': 'sum'
            }).reset_index().sort_values('quantity', ascending=False)
            
            # Top products by quantity
            fig = px.bar(
                sales_by_product.head(10),
                x='product_name',
                y='quantity',
                title="Top Products by Quantity Sold",
                labels={"product_name": "Product", "quantity": "Units Sold"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Top products by revenue
            fig = px.bar(
                sales_by_product.sort_values('total_price', ascending=False).head(10),
                x='product_name',
                y='total_price',
                title="Top Products by Revenue",
                labels={"product_name": "Product", "total_price": "Revenue (€)"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with tab3:
            st.subheader("Store Analysis")
            
            # Sales by store
            sales_by_store = sales_data.groupby(['store_name', 'city']).agg({
                'total_price': 'sum',
                'bill_id': 'nunique',
                'quantity': 'sum'
            }).reset_index().sort_values('total_price', ascending=False)
            
            # Store sales comparison
            fig = px.bar(
                sales_by_store,
                x='store_name',
                y='total_price',
                color='city',
                title="Sales by Store",
                labels={"store_name": "Store", "total_price": "Sales (€)", "city": "City"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Transactions by store
            fig = px.bar(
                sales_by_store,
                x='store_name',
                y='bill_id',
                color='city',
                title="Transactions by Store",
                labels={"store_name": "Store", "bill_id": "Transactions", "city": "City"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
        # Show raw data expandable section
        with st.expander("View Raw Sales Data"):
            st.dataframe(sales_data.sort_values('purchase_date', ascending=False), use_container_width=True)
    else:
        st.warning("No sales data available for the selected period.")
except Exception as e:
    st.error(f"Error loading sales analysis data: {e}")

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
