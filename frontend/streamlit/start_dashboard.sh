#!/bin/bash

# Script to initialize and run the EDEKA Analytics Dashboard
# This script ensures all dependencies are installed and the environment is properly set up

# Set development mode
export EDEKA_DEV_MODE=true

# Make sure we're in the project root directory
cd "$(dirname "$0")/../.."
PROJECT_ROOT=$(pwd)

echo "=== EDEKA Analytics Dashboard Setup ==="
echo "Project root: $PROJECT_ROOT"

# Activate the virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Warning: No virtual environment found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing required packages..."
    pip install -r requirements.txt
fi

# Make sure the python path includes our project
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Initialize database if needed
echo -e "\nInitializing database..."
python -c "
import sys
sys.path.append('$PROJECT_ROOT')
import os
os.environ['EDEKA_DEV_MODE'] = 'true'

try:
    from sqlalchemy import text
    from src.utils.db_utils import get_internal_db_engine, get_db_session
    from src.utils.mock_data import get_mock_stores_data, get_mock_products_data, get_mock_customers_data, get_mock_sales_data
    
    print('Connecting to database...')
    engine = get_internal_db_engine()
    
    with get_db_session(engine) as session:
        # Check tables
        tables = ['stores', 'products', 'customers', 'sales']
        for table in tables:
            result = session.execute(text(f'SELECT COUNT(*) FROM {table}'))
            count = result.scalar()
            print(f'{table.capitalize()} table: {count} records')
            
            if count == 0:
                print(f'Initializing {table} table...')
                if table == 'stores':
                    mock_data = get_mock_stores_data(20)
                elif table == 'products':
                    mock_data = get_mock_products_data(50)
                elif table == 'customers':
                    mock_data = get_mock_customers_data(100)
                elif table == 'sales':
                    mock_data = get_mock_sales_data(500)
                
                for _, row in mock_data.iterrows():
                    record = row.to_dict()
                    columns = ', '.join(record.keys())
                    placeholders = ', '.join([f':{col}' for col in record.keys()])
                    session.execute(text(f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'), record)
                
                session.commit()
                print(f'Added {len(mock_data)} records to {table}')
    
    print('Database initialization complete!')
    
except Exception as e:
    print(f'Error initializing database: {e}')
    import traceback
    traceback.print_exc()
"

# Start the Streamlit app
echo -e "\nStarting EDEKA Analytics Dashboard..."
streamlit run frontend/streamlit/Home.py
