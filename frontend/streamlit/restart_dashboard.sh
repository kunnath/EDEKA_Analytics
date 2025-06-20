#!/bin/bash

# Restart the EDEKA Analytics Dashboard
# This script kills any running Streamlit instance and starts a fresh one

echo "Stopping any running Streamlit instances..."
pkill -f streamlit

echo "Clearing Streamlit cache..."
rm -rf ~/.streamlit/cache

echo "Starting fresh dashboard instance..."
cd /Users/kunnath/Projects/EDEKA_Stepaniak && ./frontend/streamlit/start_dashboard.sh

echo "Dashboard should be accessible at http://localhost:8501"
