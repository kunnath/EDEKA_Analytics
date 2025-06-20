# EDEKA Analytics Dashboard - Client Guide

Welcome to the EDEKA Analytics Dashboard, a powerful tool for visualizing and analyzing your retail data. This guide will help you get started and make the most of the dashboard's features.

## Accessing the Dashboard

The dashboard can be accessed in one of two ways:

1. **Using the provided URL**: If we've hosted the dashboard on a server, you'll receive a URL that you can open in any modern web browser.

2. **Running locally**: If you're running the dashboard on your own computer, use the following command in the terminal:
   ```bash
   ./frontend/streamlit/run_dashboard.sh
   ```
   This will start the dashboard and open it in your default web browser at http://localhost:8501.

## Dashboard Navigation

The dashboard is organized into several pages that you can access from the sidebar on the left:

- **Home**: Overview of key performance metrics and trends
- **Sales Analysis**: Detailed analysis of sales data with filtering options
- **Product Insights**: Product performance, inventory, and category analysis
- **Customer Analytics**: Customer segmentation and behavior patterns
- **Store Performance**: Store-level metrics and regional comparisons

## Using the Dashboard

### Interactive Features

All charts and visualizations are interactive:
- Hover over charts to see detailed information
- Click on legends to filter data
- Use the zoom and pan controls to explore specific parts of charts
- Download any chart as an image using the menu in the top-right of each chart

### Filtering Data

Each dashboard page offers various filters in the sidebar:
- **Time Period**: Adjust the date range for analysis
- **Categories**: Filter by product categories
- **Stores**: Select specific stores for analysis
- **Customer Segments**: Filter by customer segment (where applicable)

### Exporting Data

You can export data in several ways:
1. **Download CSV**: Use the download button below tables
2. **Copy to Clipboard**: Select table cells and use Ctrl+C (or Cmd+C on Mac)
3. **Export Charts**: Download charts as PNG images

## Demo Mode vs. Live Data

The dashboard can operate in two modes:

- **Demo Mode** (currently active): Uses generated sample data to demonstrate dashboard functionality without connecting to production databases.

- **Live Mode**: Connects to your actual database and displays real-time data from your stores.

## Getting Help

If you have any questions or encounter issues while using the dashboard:

1. Refer to the detailed documentation in the `frontend/streamlit/README.md` file
2. Contact the technical support team at [support@example.com](mailto:support@example.com)
3. Submit a feature request or bug report through the project's issue tracker

## Next Steps

As we continue to develop this analytics solution, we plan to add:
- More advanced predictive analytics
- Automated anomaly detection
- Customizable dashboard layouts
- Mobile-optimized views
- Integration with additional data sources
