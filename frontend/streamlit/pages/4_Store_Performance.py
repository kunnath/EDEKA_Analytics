"""
Store Performance page for the EDEKA Analytics Dashboard.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys

# Add project root to Python path
sys.path.append('/Users/kunnath/Projects/EDEKA_Stepaniak')

from frontend.streamlit.utils import get_store_data, get_store_performance, get_sales_data

# Page configuration
st.set_page_config(
    page_title="EDEKA Store Performance",
    page_icon="🏪",
    layout="wide"
)

# Sidebar
st.sidebar.title("Store Performance")
st.sidebar.write("Analyze store metrics and performance.")

# Time period filter
time_period = st.sidebar.slider(
    "Analysis Period (days)",
    min_value=7,
    max_value=365,
    value=90,
    step=7
)

# Main content
st.title("Store Performance")
st.write("Compare store metrics, regional performance, and operational insights.")

try:
    # Get store data
    store_data = get_store_data()
    store_performance = get_store_performance()
    
    if not store_data.empty and not store_performance.empty:
        # Merge store data with performance metrics
        store_analysis = pd.merge(store_data, store_performance, left_on=['name', 'city'], right_on=['store_name', 'city'], how='left')
        
        # Fill NaN values for stores with no sales
        store_analysis.fillna({'num_transactions': 0, 'total_sales': 0}, inplace=True)
        
        # Calculate average transaction value
        store_analysis['avg_transaction'] = store_analysis.apply(
            lambda row: row['total_sales'] / row['num_transactions'] if row['num_transactions'] > 0 else 0,
            axis=1
        )
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_stores = len(store_data)
        total_sales = store_analysis['total_sales'].sum()
        total_transactions = store_analysis['num_transactions'].sum()
        avg_sales_per_store = total_sales / total_stores if total_stores > 0 else 0
        
        col1.metric("Total Stores", f"{total_stores:,}")
        col2.metric("Total Sales", f"€{total_sales:,.2f}")
        col3.metric("Total Transactions", f"{total_transactions:,}")
        col4.metric("Avg. Sales per Store", f"€{avg_sales_per_store:,.2f}")
        
        # Create tabs for different visualizations
        tab1, tab2, tab3 = st.tabs(["Sales Performance", "Regional Analysis", "Store Comparison"])
        
        with tab1:
            st.subheader("Store Sales Performance")
            
            # Store sales ranking
            fig = px.bar(
                store_analysis.sort_values('total_sales', ascending=False),
                x='name',
                y='total_sales',
                color='city',
                title="Total Sales by Store",
                labels={"name": "Store", "total_sales": "Sales (€)", "city": "City"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Transactions by store
            fig = px.bar(
                store_analysis.sort_values('num_transactions', ascending=False),
                x='name',
                y='num_transactions',
                color='city',
                title="Number of Transactions by Store",
                labels={"name": "Store", "num_transactions": "Transactions", "city": "City"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Average transaction value
            fig = px.bar(
                store_analysis.sort_values('avg_transaction', ascending=False),
                x='name',
                y='avg_transaction',
                color='city',
                title="Average Transaction Value by Store",
                labels={"name": "Store", "avg_transaction": "Avg. Transaction (€)", "city": "City"}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("Regional Analysis")
            
            # Sales by city
            city_performance = store_analysis.groupby('city').agg({
                'total_sales': 'sum',
                'num_transactions': 'sum',
                'store_id': 'count'
            }).reset_index()
            
            city_performance.columns = ['City', 'Total Sales', 'Transactions', 'Store Count']
            city_performance['Sales per Store'] = city_performance['Total Sales'] / city_performance['Store Count']
            city_performance['Avg. Transaction'] = city_performance['Total Sales'] / city_performance['Transactions']
            
            # Sales by city
            fig = px.bar(
                city_performance.sort_values('Total Sales', ascending=False),
                x='City',
                y='Total Sales',
                title="Total Sales by City",
                labels={"Total Sales": "Sales (€)"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Sales per store by city
            fig = px.bar(
                city_performance.sort_values('Sales per Store', ascending=False),
                x='City',
                y='Sales per Store',
                title="Sales per Store by City",
                labels={"Sales per Store": "Sales per Store (€)"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # City comparison table
            st.subheader("City Performance Comparison")
            st.dataframe(city_performance.sort_values('Total Sales', ascending=False), use_container_width=True)
        
        with tab3:
            st.subheader("Store Comparison")
            
            # Allow comparing specific stores
            selected_stores = st.multiselect(
                "Select stores to compare:",
                options=store_analysis['name'].unique(),
                default=store_analysis.sort_values('total_sales', ascending=False)['name'].head(5).tolist()
            )
            
            if selected_stores:
                comparison_data = store_analysis[store_analysis['name'].isin(selected_stores)]
                
                # Create a radar chart for store comparison
                categories = ['Total Sales', 'Transactions', 'Avg. Transaction']
                
                fig = go.Figure()
                
                for i, store in enumerate(comparison_data['name']):
                    store_row = comparison_data[comparison_data['name'] == store].iloc[0]
                    
                    # Normalize values for radar chart
                    sales_norm = store_row['total_sales'] / comparison_data['total_sales'].max()
                    trans_norm = store_row['num_transactions'] / comparison_data['num_transactions'].max()
                    avg_norm = store_row['avg_transaction'] / comparison_data['avg_transaction'].max()
                    
                    fig.add_trace(go.Scatterpolar(
                        r=[sales_norm, trans_norm, avg_norm],
                        theta=categories,
                        fill='toself',
                        name=store
                    ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1]
                        )
                    ),
                    title="Store Performance Comparison (Normalized)",
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Raw comparison data
                comparison_table = comparison_data[['name', 'city', 'total_sales', 'num_transactions', 'avg_transaction']]
                comparison_table.columns = ['Store', 'City', 'Total Sales (€)', 'Transactions', 'Avg. Transaction (€)']
                
                st.subheader("Comparison Data")
                st.dataframe(comparison_table.sort_values('Total Sales (€)', ascending=False), use_container_width=True)
            else:
                st.warning("Please select at least one store to compare.")
        
        # Sales trends over time
        st.subheader("Sales Trends by Store")
        
        # Get sales data for time trend
        sales_data = get_sales_data(time_period)
        
        if not sales_data.empty:
            # Allow selecting stores for trend analysis
            trend_stores = st.multiselect(
                "Select stores for trend analysis:",
                options=store_analysis['name'].unique(),
                default=store_analysis.sort_values('total_sales', ascending=False)['name'].head(3).tolist(),
                key="trend_stores"
            )
            
            if trend_stores:
                # Filter for selected stores
                trend_data = sales_data[sales_data['store_name'].isin(trend_stores)]
                
                # Group by store and date
                trend_data['date'] = pd.to_datetime(trend_data['purchase_date']).dt.date
                store_trends = trend_data.groupby(['store_name', 'date']).agg({
                    'total_price': 'sum'
                }).reset_index()
                
                # Plot trend lines
                fig = px.line(
                    store_trends,
                    x='date',
                    y='total_price',
                    color='store_name',
                    title="Daily Sales Trend by Store",
                    labels={"date": "Date", "total_price": "Sales (€)", "store_name": "Store"}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Please select at least one store for trend analysis.")
        else:
            st.warning("No sales data available for trend analysis.")
        
        # Store details
        st.subheader("Store Details")
        
        # Store selector
        selected_store = st.selectbox(
            "Select a store to view details:",
            options=store_data['name'].tolist()
        )
        
        if selected_store:
            store_details = store_data[store_data['name'] == selected_store].iloc[0]
            store_metrics = store_analysis[store_analysis['name'] == selected_store].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"{store_details['name']}")
                st.write(f"**ID:** {store_details['store_id']}")
                st.write(f"**Location:** {store_details['city']}")
                st.write(f"**Postal Code:** {store_details['postal_code']}")
            
            with col2:
                st.subheader("Performance Metrics")
                st.write(f"**Total Sales:** €{store_metrics['total_sales']:,.2f}")
                st.write(f"**Transactions:** {store_metrics['num_transactions']:,}")
                st.write(f"**Avg. Transaction:** €{store_metrics['avg_transaction']:,.2f}")
    else:
        st.warning("No store data available. Please ensure the database is properly initialized with store data.")
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
