# EDEKA Analytics Database Integration Module

This module provides functionality to synchronize data between an external database (MySQL/PostgreSQL) and the internal EDEKA analytics database.

## Features

- Connect to both external and internal databases using SQLAlchemy
- Fetch product sales, customer, and product data from external sources
- Transform data according to configured mappings
- Insert or update data in the internal database
- Log errors and sync summaries
- Scheduled synchronization with configurable intervals
- Support for incremental sync using timestamp columns
- Interactive Streamlit dashboard for data visualization and analytics

## Directory Structure

```
EDEKA_Stepaniak/
├── config/
│   └── config.yaml       # Configuration for DB connections and mappings
├── frontend/
│   └── streamlit/        # Streamlit dashboard application
│       ├── pages/        # Dashboard pages for different analytics views
│       ├── app.py        # Main dashboard application
│       ├── Home.py       # Home page of dashboard
│       ├── utils.py      # Dashboard utility functions
│       └── initialize_data.py # Data initialization script
├── logs/                 # Sync logs directory
├── src/
│   ├── integrations/     # Data integration modules
│   │   ├── external_db_sync.py
│   │   └── scheduler.py
│   ├── models/           # Database models
│   │   └── database.py
│   ├── utils/            # Utility functions
│   │   ├── db_utils.py
│   │   ├── logger.py
│   │   └── mock_data.py  # Mock data generator for development
│   └── main.py           # Main entry point
├── venv/                 # Python virtual environment
├── .env                  # Environment variables
└── requirements.txt      # Python dependencies
```

## Installation

1. Create a Python virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the database connections by editing the `.env` file:
   ```
   INTERNAL_DB_HOST=localhost
   INTERNAL_DB_PORT=5432
   INTERNAL_DB_NAME=edeka_analytics
   INTERNAL_DB_USER=edeka_user
   INTERNAL_DB_PASSWORD=your_secure_password

   EXTERNAL_DB_HOST=external-server.example.com
   EXTERNAL_DB_PORT=3306
   EXTERNAL_DB_NAME=external_sales_db
   EXTERNAL_DB_USER=external_user
   EXTERNAL_DB_PASSWORD=external_password
   
   # Set to 'true' to use mock data instead of connecting to external DB
   EDEKA_DEV_MODE=true
   ```

5. Configure table mappings in `config/config.yaml`

## Usage

### Initialize the Database

Before the first run, initialize the database schema:

```bash
python -m src.main init
```

### One-Time Sync

To run a one-time synchronization of all tables:

```bash
python -m src.main sync
```

To sync a specific table:

```bash
python -m src.main sync --table sales
```

### Start the Scheduler

To start the sync scheduler (which will run sync jobs at regular intervals):

```bash
python -m src.main scheduler
```

## Development Mode

For development and testing without a real external database connection, set:

```
EDEKA_DEV_MODE=true
```

In development mode, the system will use mock data generated locally instead of trying to connect to an external database.

## Analytics Dashboard

The project includes a Streamlit-based analytics dashboard for visualizing the synchronized data. The dashboard provides insights into sales, products, customers, and store performance.

### Running the Dashboard

To run the dashboard:

```bash
./frontend/streamlit/run_dashboard.sh
```

Or manually:

```bash
# Set development mode
export EDEKA_DEV_MODE=true

# Initialize data if needed
python -m frontend.streamlit.initialize_data

# Start the dashboard
streamlit run frontend/streamlit/Home.py
```

The dashboard includes:
- Overview of key metrics
- Sales analysis with trend charts
- Product insights and category analysis
- Customer segmentation and behavior analytics
- Store performance comparison
# EDEKA_Analytics
