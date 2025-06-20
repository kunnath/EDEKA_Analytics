"""
Mock data provider for testing and development.
This module provides sample data for testing the synchronization functionality
without requiring a connection to an external database.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def get_mock_sales_data(num_records=100):
    """Generate mock sales data."""
    # Generate product IDs from 1-50 to ensure they exist in the products table
    product_ids = list(range(1, 51))
    # Generate customer IDs from 1-100 to ensure they exist in the customers table
    customer_ids = list(range(1, 101))
    
    data = {
        'bill_id': [f'INV-{i:06d}' for i in range(1, num_records + 1)],
        'product_id': [random.choice(product_ids) for _ in range(num_records)],
        'customer_id': [random.choice(customer_ids) for _ in range(num_records)],
        'quantity': [random.randint(1, 10) for _ in range(num_records)],
        'unit_price': [round(random.uniform(1.0, 100.0), 2) for _ in range(num_records)],
        'store_id': [random.randint(1, 20) for _ in range(num_records)],
        'purchase_date': [(datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d %H:%M:%S') for _ in range(num_records)]
    }
    
    # Calculate total amount
    data['total_price'] = [data['unit_price'][i] * data['quantity'][i] for i in range(num_records)]
    
    return pd.DataFrame(data)

def get_mock_products_data(num_records=100):
    """Generate mock products data."""
    # Use category IDs 1-10 as integers to match the database schema
    category_ids = list(range(1, 11))  # Categories 1-10
    
    data = {
        'product_id': list(range(1, num_records + 1)),
        'name': [f'Product {i}' for i in range(1, num_records + 1)],
        'category_id': [random.choice(category_ids) for _ in range(num_records)],
        'price': [round(random.uniform(1.0, 100.0), 2) for _ in range(num_records)],
        'description': [f'Description for product {i}' for i in range(1, num_records + 1)],
        'created_at': [(datetime.now() - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d %H:%M:%S') for _ in range(num_records)],
        'updated_at': [datetime.now().strftime('%Y-%m-%d %H:%M:%S') for _ in range(num_records)]
    }
    
    return pd.DataFrame(data)

def get_mock_customers_data(num_records=100):
    """Generate mock customer data."""
    first_names = ['John', 'Jane', 'Michael', 'Emma', 'William', 'Olivia', 'James', 'Sophia', 'Robert', 'Charlotte']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller', 'Davis', 'Wilson', 'Taylor', 'Clark']
    
    data = {
        'customer_id': list(range(1, num_records + 1)),
        'first_name': [random.choice(first_names) for _ in range(num_records)],
        'last_name': [random.choice(last_names) for _ in range(num_records)],
        'email': [f'customer{i}@example.com' for i in range(1, num_records + 1)],
        'phone': [f'555-{random.randint(100, 999)}-{random.randint(1000, 9999)}' for _ in range(num_records)],
        'address': [f'{random.randint(1, 999)} Main St, City {i}' for i in range(1, num_records + 1)],
        'registration_date': [(datetime.now() - timedelta(days=random.randint(1, 730))).strftime('%Y-%m-%d %H:%M:%S') for _ in range(num_records)],
        'last_purchase_date': [(datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d %H:%M:%S') for _ in range(num_records)]
    }
    
    return pd.DataFrame(data)

def get_mock_stores_data(num_records=20):
    """Generate mock store data."""
    cities = ['Berlin', 'Hamburg', 'Munich', 'Cologne', 'Frankfurt', 'Stuttgart', 'Düsseldorf', 'Leipzig', 'Dortmund', 'Essen']
    
    data = {
        'store_id': list(range(1, num_records + 1)),
        'name': [f'EDEKA Store {i}' for i in range(1, num_records + 1)],
        'address': [f'{random.randint(1, 999)} Hauptstraße' for _ in range(num_records)],
        'city': [random.choice(cities) for _ in range(num_records)],
        'postal_code': [f'{random.randint(10000, 99999)}' for _ in range(num_records)],
        'phone': [f'+49-{random.randint(100, 999)}-{random.randint(1000000, 9999999)}' for _ in range(num_records)]
    }
    
    return pd.DataFrame(data)

def get_mock_data(table_name, num_records=100):
    """Get mock data for the specified table."""
    if table_name == 'sales':
        return get_mock_sales_data(num_records)
    elif table_name == 'products':
        return get_mock_products_data(num_records)
    elif table_name == 'customers':
        return get_mock_customers_data(num_records)
    elif table_name == 'stores':
        return get_mock_stores_data(20)  # We only need 20 stores
    else:
        raise ValueError(f"No mock data available for table: {table_name}")
