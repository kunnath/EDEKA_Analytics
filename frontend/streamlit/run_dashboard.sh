#!/bin/bash

# Initialize the environment variables
export EDEKA_DEV_MODE=true

# Make sure we're in the project root directory
cd "$(dirname "$0")/../.."

# Activate the virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Warning: No virtual environment found. Please run:"
    echo "python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Initialize store data if needed
echo "Initializing store data..."
python -m frontend.streamlit.initialize_data

# Start the Streamlit app
echo "Starting EDEKA Analytics Dashboard..."
streamlit run frontend/streamlit/Home.py
