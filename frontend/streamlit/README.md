# EDEKA Analytics Dashboard

A Streamlit-based analytics dashboard for visualizing EDEKA sales, products, customer, and store data.

## Overview

This dashboard provides comprehensive analytics and insights for EDEKA retail operations. It includes several views:

- **Home**: A high-level overview of key performance indicators
- **Sales Analysis**: Detailed analysis of sales trends and patterns
- **Product Insights**: Information about product performance and inventory
- **Customer Analytics**: Customer segmentation and behavior analysis
- **Store Performance**: Store-level metrics and regional performance

## Prerequisites

- Python 3.8 or higher
- Required Python packages (see requirements.txt)
- PostgreSQL database with EDEKA analytics data

## Installation

1. Make sure all required packages are installed:
   ```
   pip3 install -r requirements.txt
   ```

2. Configure database connection in `.env` file.

## Running the Dashboard

For convenience, a shell script is provided to run the dashboard:

```bash
./frontend/streamlit/run_dashboard.sh
```

This script will:
1. Set up the development mode (using mock data)
2. Initialize any missing data if needed
3. Start the Streamlit server

Alternatively, you can run these steps manually:

```bash
# Set development mode
export EDEKA_DEV_MODE=true

# Initialize data if needed
python3 -m frontend.streamlit.initialize_data

# Start the dashboard
streamlit run frontend/streamlit/Home.py
```

## Development Mode

When `EDEKA_DEV_MODE=true` is set, the application will use mock data for demonstration purposes, avoiding the need for an external database connection.

## Data Sources

The dashboard connects to the internal PostgreSQL database and queries the following tables:
- `sales`
- `products`
- `customers`
- `stores`

## Customization

To modify the dashboard's appearance or functionality:
- Edit the main page in `frontend/streamlit/Home.py`
- Edit specific pages in the `frontend/streamlit/pages/` directory
- Modify data access functions in `frontend/streamlit/utils.py`
