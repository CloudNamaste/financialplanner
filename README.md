# Financial Planner - RSU Manager

A Streamlit-based web application designed to help users manage their Restricted Stock Units (RSUs). It provides tools for tracking vesting schedules, managing sales, calculating tax implications, and generating reports.

## Features

- **RSU Vesting Schedule**: Track and manage RSU vestings with tax calculations
- **RSU Sell Tracker**: Record and analyze RSU sales with capital gains calculations
- **Financial Summaries**: Generate comprehensive financial summaries by fiscal year
- **EOY Tax Return Assistant**: Prepare tax return information with ATO-specific guidance
- **Tax Optimization Engine**: (Coming soon) Get recommendations for tax-efficient RSU management

## Getting Started

### Prerequisites

- Python 3.x
- Required packages: streamlit, pandas, openpyxl, fpdf, matplotlib

### Installation

1. Clone the repository or download the source code
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

1. Navigate to the project directory
2. Run the Streamlit application:
   ```
   streamlit run app.py
   ```
3. Access the application in your web browser at the provided URL (typically http://localhost:8501)

## Usage

### Loading Data

You have three options for working with data:

1. **Load Sample Data**: Click the "Load Sample Data" button to load pre-configured sample data
2. **Upload Excel Files**: Upload your own Excel files for vesting schedule and sales data
3. **Manual Entry**: Add entries directly in the application using the "Add New" buttons

### Vesting Schedule

- View and manage your RSU vesting schedule
- Add new vesting entries using the "Add New Vesting Entry" button
- Edit existing entries directly in the data grid
- Download the vesting schedule as an Excel file

### RSU Sell Tracker

- Record and track RSU sales
- Add new sales entries using the "Add New Sales Entry" button
- Edit existing entries directly in the data grid
- View capital gains visualization
- Download sales data as an Excel file

### Summary

- View financial summaries of your RSU vestings and sales
- See breakdowns by financial year
- Export summaries to PDF

### EOY Tax Return Assistant

- Select a financial year to generate tax return information
- View income and tax summaries
- See ATO tax return item codes for easy tax filing
- Export tax summaries in Excel or PDF format

## Data Format

### Vesting Schedule Format

The application expects the following columns in the vesting schedule:
- Vesting Date or Vested Date (date format)
- RSU Vested or RSUs Vested (number)
- Price at Vesting or FMV at Vesting (number)

### Sales Data Format

The application expects the following columns in the sales data:
- Sell Date (date format)
- Shares Sold (number)
- Sale Price (number)
- FMV at Vesting (number)
- Held > 12 Months (boolean)

## Australian Tax Specifics

The application includes Australian tax specifics:
- Progressive tax rates
- Medicare levy and surcharge calculations
- HECS/HELP repayment calculations
- Capital gains tax with 50% discount for long-term holdings
- Financial year determination (July-June)

## Troubleshooting

If you encounter issues:

1. Ensure your Excel files have the expected column names (or similar variations)
2. Check that date columns are in a recognizable date format
3. Verify that numeric columns contain valid numbers
4. If data appears incorrect, try clearing and re-entering the data

## License

This project is licensed under the MIT License - see the LICENSE file for details.
