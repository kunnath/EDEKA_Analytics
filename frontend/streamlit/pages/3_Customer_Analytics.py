"""
Customer Analytics page for the EDEKA Analytics Dashboard.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sys

# Add project root to Python path
sys.path.append('/Users/kunnath/Projects/EDEKA_Stepaniak')

from frontend.streamlit.utils import get_customer_data, get_sales_data, get_customer_segments

# Page configuration
st.set_page_config(
    page_title="EDEKA Customer Analytics",
    page_icon="👥",
    layout="wide"
)

# Sidebar
st.sidebar.title("Customer Analytics")
st.sidebar.write("Analyze customer behavior and demographics.")

# Time period filter
time_period = st.sidebar.slider(
    "Sales Analysis Period (days)",
    min_value=7,
    max_value=365,
    value=90,
    step=7
)

# Main content
st.title("Customer Analytics")
st.write("Understand customer behavior, demographics, and purchase patterns.")

try:
    # Get customer data
    customer_data = get_customer_data()
    
    if not customer_data.empty:
        # Pre-process dates
        customer_data['registration_date'] = pd.to_datetime(customer_data['registration_date'])
        customer_data['last_purchase_date'] = pd.to_datetime(customer_data['last_purchase_date'])
        
        # Calculate recency
        customer_data['days_since_last_purchase'] = (datetime.now() - customer_data['last_purchase_date']).dt.days
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_customers = len(customer_data)
        new_customers_30d = len(customer_data[customer_data['registration_date'] >= datetime.now() - timedelta(days=30)])
        active_customers = len(customer_data[customer_data['days_since_last_purchase'] <= 30])
        inactive_customers = len(customer_data[customer_data['days_since_last_purchase'] > 180])
        
        col1.metric("Total Customers", f"{total_customers:,}")
        col2.metric("New Customers (30d)", f"{new_customers_30d:,}")
        col3.metric("Active Customers", f"{active_customers:,}")
        col4.metric("Inactive Customers", f"{inactive_customers:,}")
        
        # Create tabs for different visualizations
        tab1, tab2, tab3 = st.tabs(["Customer Overview", "Segmentation", "Purchase Behavior"])
        
        with tab1:
            st.subheader("Customer Overview")
            
            # Customer registration over time
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
            
            # Customer last purchase recency
            recency_groups = [
                (0, 30, 'Active (0-30 days)'),
                (31, 90, 'Recent (31-90 days)'),
                (91, 180, 'Lapsed (91-180 days)'),
                (181, 365, 'Inactive (181-365 days)'),
                (366, float('inf'), 'Lost (366+ days)')
            ]
            
            customer_data['recency_group'] = None
            for min_days, max_days, group_name in recency_groups:
                mask = (customer_data['days_since_last_purchase'] >= min_days) & (customer_data['days_since_last_purchase'] <= max_days)
                customer_data.loc[mask, 'recency_group'] = group_name
            
            recency_counts = customer_data.groupby('recency_group').size().reset_index(name='count')
            
            fig = px.pie(
                recency_counts,
                values='count',
                names='recency_group',
                title="Customer Recency Analysis",
                color_discrete_sequence=px.colors.sequential.RdBu_r
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("Customer Segmentation")
            
            try:
                # Get customer segments using the utility function
                customer_segments = get_customer_segments()
                
                if not customer_segments.empty:
                    # Show segmentation distribution
                    segment_counts = customer_segments.groupby('segment').size().reset_index(name='count')
                    
                    fig = px.pie(
                        segment_counts,
                        values='count',
                        names='segment',
                        title="Customer Segments Distribution",
                        color_discrete_sequence=px.colors.qualitative.Set1
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show segment characteristics
                    segments_summary = customer_segments.groupby('segment').agg({
                        'days_since_purchase': 'mean',
                        'num_transactions': 'mean',
                        'total_spend': 'mean',
                        'customer_id': 'count'
                    }).reset_index()
                    
                    segments_summary.columns = ['Segment', 'Avg. Recency (days)', 'Avg. Frequency', 'Avg. Spend (€)', 'Customer Count']
                    segments_summary = segments_summary.sort_values('Customer Count', ascending=False)
                    
                    st.subheader("Segment Characteristics")
                    st.dataframe(segments_summary, use_container_width=True)
                    
                    # Show top customers
                    st.subheader("Top Customers by Spend")
                    top_customers = customer_segments.sort_values('total_spend', ascending=False).head(10)
                    
                    fig = px.bar(
                        top_customers,
                        x='total_spend',
                        y=top_customers['first_name'] + ' ' + top_customers['last_name'],
                        orientation='h',
                        title="Top 10 Customers by Total Spend",
                        labels={"total_spend": "Total Spend (€)", "y": "Customer"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No customer segment data available.")
            except Exception as e:
                st.error(f"Error loading customer segment data: {e}")
                # Fallback to old method using sales data
                # Get sales data for RFM analysis
                st.warning("Falling back to basic segmentation method...")
                sales_data = get_sales_data(time_period)
                
                if not sales_data.empty:
                    # Prepare data for RFM
                    customer_purchase_data = sales_data.groupby(['customer_id', 'first_name', 'last_name']).agg({
                        'purchase_date': 'max',  # Recency - last purchase date
                        'bill_id': 'nunique',  # Frequency - number of transactions
                        'total_price': 'sum'  # Monetary - total spend
                    }).reset_index()
                    
                    customer_purchase_data.columns = ['customer_id', 'first_name', 'last_name', 'last_purchase', 'frequency', 'monetary']
                    
                    # Calculate recency in days
                    customer_purchase_data['recency'] = (datetime.now() - pd.to_datetime(customer_purchase_data['last_purchase'])).dt.days
                    
                    # Create RFM segments
                    def get_recency_score(days):
                        if days <= 30:
                            return 5
                        elif days <= 60:
                            return 4
                        elif days <= 90:
                            return 3
                        elif days <= 180:
                            return 2
                        else:
                            return 1
                    
                    def get_frequency_score(freq):
                        if freq >= 10:
                            return 5
                        elif freq >= 7:
                            return 4
                        elif freq >= 5:
                            return 3
                        elif freq >= 3:
                            return 2
                        else:
                            return 1
                    
                    def get_monetary_score(amount):
                        if amount >= 1000:
                            return 5
                        elif amount >= 750:
                            return 4
                        elif amount >= 500:
                            return 3
                        elif amount >= 250:
                            return 2
                        else:
                            return 1
                    
                    customer_purchase_data['r_score'] = customer_purchase_data['recency'].apply(get_recency_score)
                    customer_purchase_data['f_score'] = customer_purchase_data['frequency'].apply(get_frequency_score)
                    customer_purchase_data['m_score'] = customer_purchase_data['monetary'].apply(get_monetary_score)
                    
                    # Calculate RFM score
                    customer_purchase_data['rfm_score'] = customer_purchase_data['r_score'] + customer_purchase_data['f_score'] + customer_purchase_data['m_score']
                    
                    # Create segments
                    def get_segment(score):
                        if score >= 13:
                            return 'Champions'
                        elif score >= 10:
                            return 'Loyal Customers'
                        elif score >= 7:
                            return 'Potential Loyalists'
                        elif score >= 5:
                            return 'At Risk'
                        else:
                            return 'Needs Attention'
                    
                    customer_purchase_data['segment'] = customer_purchase_data['rfm_score'].apply(get_segment)
                    
                    # Show segmentation distribution
                    segment_counts = customer_purchase_data.groupby('segment').size().reset_index(name='count')
                    
                    fig = px.pie(
                        segment_counts,
                        values='count',
                        names='segment',
                        title="Customer Segments Distribution",
                        color_discrete_sequence=px.colors.qualitative.Set1
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show segment characteristics
                    segments_summary = customer_purchase_data.groupby('segment').agg({
                        'recency': 'mean',
                        'frequency': 'mean',
                        'monetary': 'mean',
                        'customer_id': 'count'
                    }).reset_index()
                    
                    segments_summary.columns = ['Segment', 'Avg. Recency (days)', 'Avg. Frequency', 'Avg. Spend (€)', 'Customer Count']
                    segments_summary = segments_summary.sort_values('Customer Count', ascending=False)
                    
                    st.subheader("Segment Characteristics")
                    st.dataframe(segments_summary, use_container_width=True)
                    
                    # Show top customers
                    st.subheader("Top Customers by Spend")
                    top_customers = customer_purchase_data.sort_values('monetary', ascending=False).head(10)
                    
                    fig = px.bar(
                        top_customers,
                        x='monetary',
                        y=top_customers['first_name'] + ' ' + top_customers['last_name'],
                        orientation='h',
                        title="Top 10 Customers by Total Spend",
                        labels={"monetary": "Total Spend (€)", "y": "Customer"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No sales data available for customer segmentation.")
                segments_summary = customer_purchase_data.groupby('segment').agg({
                    'recency': 'mean',
                    'frequency': 'mean',
                    'monetary': 'mean',
                    'customer_id': 'count'
                }).reset_index()
                
                segments_summary.columns = ['Segment', 'Avg. Recency (days)', 'Avg. Frequency', 'Avg. Spend (€)', 'Customer Count']
                segments_summary = segments_summary.sort_values('Customer Count', ascending=False)
                
                st.subheader("Segment Characteristics")
                st.dataframe(segments_summary, use_container_width=True)
                
                # Show top customers
                st.subheader("Top Customers by Spend")
                top_customers = customer_purchase_data.sort_values('monetary', ascending=False).head(10)
                
                fig = px.bar(
                    top_customers,
                    x='monetary',
                    y=top_customers['first_name'] + ' ' + top_customers['last_name'],
                    orientation='h',
                    title="Top 10 Customers by Total Spend",
                    labels={"monetary": "Total Spend (€)", "y": "Customer"}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No sales data available for customer segmentation.")
        
        with tab3:
            st.subheader("Purchase Behavior")
            
            # Get sales data for purchase analysis
            sales_data = get_sales_data(time_period)
            
            if not sales_data.empty:
                # Transaction frequency
                customer_transactions = sales_data.groupby(['customer_id', 'first_name', 'last_name'])['bill_id'].nunique().reset_index()
                customer_transactions.columns = ['customer_id', 'first_name', 'last_name', 'transaction_count']
                
                # Group by transaction count
                transaction_groups = [
                    (1, '1 transaction'),
                    (2, '2 transactions'),
                    (3, '3 transactions'),
                    (4, '4 transactions'),
                    (5, '5 transactions'),
                    (float('inf'), '6+ transactions')
                ]
                
                customer_transactions['transaction_group'] = '6+ transactions'
                for count, group_name in transaction_groups:
                    if count < 6:
                        customer_transactions.loc[customer_transactions['transaction_count'] == count, 'transaction_group'] = group_name
                
                transaction_group_counts = customer_transactions.groupby('transaction_group').size().reset_index(name='count')
                
                # Order the groups properly
                transaction_order = ['1 transaction', '2 transactions', '3 transactions', '4 transactions', '5 transactions', '6+ transactions']
                transaction_group_counts['transaction_group'] = pd.Categorical(transaction_group_counts['transaction_group'], categories=transaction_order, ordered=True)
                transaction_group_counts = transaction_group_counts.sort_values('transaction_group')
                
                fig = px.bar(
                    transaction_group_counts,
                    x='transaction_group',
                    y='count',
                    title="Customer Transaction Frequency",
                    labels={"transaction_group": "Number of Transactions", "count": "Number of Customers"}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Average spend per customer
                customer_spend = sales_data.groupby(['customer_id', 'first_name', 'last_name'])['total_price'].sum().reset_index()
                customer_spend.columns = ['customer_id', 'first_name', 'last_name', 'total_spend']
                
                # Create spend bands
                spend_bands = [
                    (0, 100, '€0-100'),
                    (100, 250, '€100-250'),
                    (250, 500, '€250-500'),
                    (500, 1000, '€500-1000'),
                    (1000, float('inf'), '€1000+')
                ]
                
                customer_spend['spend_band'] = None
                for min_spend, max_spend, band_name in spend_bands:
                    mask = (customer_spend['total_spend'] > min_spend) & (customer_spend['total_spend'] <= max_spend)
                    customer_spend.loc[mask, 'spend_band'] = band_name
                
                spend_band_counts = customer_spend.groupby('spend_band').size().reset_index(name='count')
                
                # Order the bands properly
                spend_order = ['€0-100', '€100-250', '€250-500', '€500-1000', '€1000+']
                spend_band_counts['spend_band'] = pd.Categorical(spend_band_counts['spend_band'], categories=spend_order, ordered=True)
                spend_band_counts = spend_band_counts.sort_values('spend_band')
                
                fig = px.bar(
                    spend_band_counts,
                    x='spend_band',
                    y='count',
                    title="Customer Spend Distribution",
                    labels={"spend_band": "Spend Range", "count": "Number of Customers"}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No sales data available for purchase behavior analysis.")
        
        # Customer search
        st.subheader("Customer Search")
        
        search_term = st.text_input("Search for customers by name:")
        
        if search_term:
            filtered_customers = customer_data[
                customer_data['first_name'].str.contains(search_term, case=False) | 
                customer_data['last_name'].str.contains(search_term, case=False)
            ]
            
            if not filtered_customers.empty:
                st.dataframe(filtered_customers, use_container_width=True)
            else:
                st.warning(f"No customers found matching '{search_term}'")
        
        # Show customer sample
        with st.expander("View Customer Sample"):
            st.dataframe(customer_data.sample(min(100, len(customer_data))), use_container_width=True)
    else:
        st.warning("No customer data available. Please ensure the database is properly initialized with customer data.")
except Exception as e:
    st.error(f"Error loading customer analytics data: {e}")

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
