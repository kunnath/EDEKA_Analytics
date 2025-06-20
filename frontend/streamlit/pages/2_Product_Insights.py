"""
Product Insights page for the EDEKA Analytics Dashboard.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import sys

# Add project root to Python path
sys.path.append('/Users/kunnath/Projects/EDEKA_Stepaniak')

from frontend.streamlit.utils import get_product_data, get_top_products, get_category_sales, CATEGORY_MAPPING

# Page configuration
st.set_page_config(
    page_title="EDEKA Product Insights",
    page_icon="📦",
    layout="wide"
)

# Sidebar
st.sidebar.title("Product Insights")
st.sidebar.write("Analyze product performance and inventory metrics.")

# Main content
st.title("Product Insights")
st.write("Explore product performance, inventory, and category analysis.")

try:
    # Get product data
    product_data = get_product_data()
    
    if not product_data.empty:
        # Add category name column
        product_data['category_name'] = product_data['category_id'].map(CATEGORY_MAPPING)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_products = len(product_data)
        avg_price = product_data['price'].mean()
        categories = product_data['category_id'].nunique()
        max_price = product_data['price'].max()
        
        col1.metric("Total Products", f"{total_products:,}")
        col2.metric("Average Price", f"€{avg_price:.2f}")
        col3.metric("Product Categories", f"{categories}")
        col4.metric("Highest Price", f"€{max_price:.2f}")
        
        # Create tabs for different visualizations
        tab1, tab2, tab3 = st.tabs(["Category Analysis", "Price Analysis", "Top Products"])
        
        with tab1:
            st.subheader("Products by Category")
            
            # Products by category
            products_by_category = product_data.groupby(['category_id', 'category_name']).size().reset_index(name='count')
            
            fig = px.bar(
                products_by_category.sort_values('count', ascending=False),
                x='category_name',
                y='count',
                title="Number of Products by Category",
                labels={"category_name": "Category", "count": "Number of Products"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Category distribution
            fig = px.pie(
                products_by_category,
                values='count',
                names='category_name',
                title="Product Distribution by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Average price by category
            avg_price_by_category = product_data.groupby(['category_id', 'category_name'])['price'].mean().reset_index()
            
            fig = px.bar(
                avg_price_by_category.sort_values('price', ascending=False),
                x='category_name',
                y='price',
                title="Average Price by Category",
                labels={"category_name": "Category", "price": "Average Price (€)"}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("Price Analysis")
            
            # Price distribution
            fig = px.histogram(
                product_data,
                x='price',
                nbins=20,
                title="Product Price Distribution",
                labels={"price": "Price (€)"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Price range by category
            fig = px.box(
                product_data,
                x='category_name',
                y='price',
                title="Price Range by Category",
                labels={"category_name": "Category", "price": "Price (€)"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Price scatter plot
            fig = px.scatter(
                product_data,
                x='product_id',
                y='price',
                color='category_name',
                hover_name='name',
                title="Price Scatter Plot by Product ID",
                labels={"product_id": "Product ID", "price": "Price (€)", "category_name": "Category"}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Top Selling Products")
            
            # Top products by sales
            top_products = get_top_products(20)
            
            if not top_products.empty:
                # Top products by units sold
                fig = px.bar(
                    top_products.sort_values('units_sold', ascending=False),
                    x='product_name',
                    y='units_sold',
                    title="Top Products by Units Sold",
                    labels={"product_name": "Product", "units_sold": "Units Sold"}
                )
                fig.update_layout(xaxis={'categoryorder':'total descending'})
                st.plotly_chart(fig, use_container_width=True)
                
                # Top products by revenue
                fig = px.bar(
                    top_products.sort_values('total_revenue', ascending=False),
                    x='product_name',
                    y='total_revenue',
                    title="Top Products by Revenue",
                    labels={"product_name": "Product", "total_revenue": "Revenue (€)"}
                )
                fig.update_layout(xaxis={'categoryorder':'total descending'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No sales data available to determine top products.")
        
        # Product search and details
        st.subheader("Product Search")
        
        search_term = st.text_input("Search for products by name:")
        
        if search_term:
            filtered_products = product_data[product_data['name'].str.contains(search_term, case=False)]
            
            if not filtered_products.empty:
                st.dataframe(filtered_products, use_container_width=True)
            else:
                st.warning(f"No products found matching '{search_term}'")
        
        # Show all products
        with st.expander("View All Products"):
            st.dataframe(product_data.sort_values('product_id'), use_container_width=True)
    else:
        st.warning("No product data available. Please ensure the database is properly initialized with product data.")
except Exception as e:
    st.error(f"Error loading product insights data: {e}")

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
