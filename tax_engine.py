"""
Tax Engine for RSU Manager
--------------------------
This module provides tax calculation functions for Australian tax specifics
related to Restricted Stock Units (RSUs).
"""

import pandas as pd
import datetime
from typing import Dict, List, Tuple, Optional, Union


# Australian Tax Brackets (FY 2024-25)
TAX_BRACKETS = {
    "2024-25": [
        {"threshold": 0, "rate": 0.0},
        {"threshold": 18201, "rate": 0.19},
        {"threshold": 45001, "rate": 0.325},
        {"threshold": 120001, "rate": 0.37},
        {"threshold": 180001, "rate": 0.45}
    ]
}

# Simplified tax configuration - removed Medicare and HELP/HECS


def calculate_income_tax(income: float, year: str = "2024-25") -> float:
    """
    Calculate income tax based on progressive tax rates
    
    Args:
        income: Taxable income
        year: Financial year for tax calculation (e.g., "2024-25")
        
    Returns:
        Calculated tax amount
    """
    brackets = TAX_BRACKETS.get(year, TAX_BRACKETS["2024-25"])
    tax = 0.0
    
    for i, bracket in enumerate(brackets):
        if i < len(brackets) - 1:
            next_threshold = brackets[i + 1]["threshold"]
            if income > bracket["threshold"]:
                taxable_in_bracket = min(income, next_threshold) - bracket["threshold"]
                tax += taxable_in_bracket * bracket["rate"]
        else:
            # Highest bracket
            if income > bracket["threshold"]:
                tax += (income - bracket["threshold"]) * bracket["rate"]
    
    return tax


# Removed Medicare and HELP/HECS calculation functions


def calculate_capital_gain(
    sale_price: float, 
    cost_base: float, 
    shares_sold: float, 
    long_term: bool = False
) -> Tuple[float, float]:
    """
    Calculate capital gain with potential 50% discount
    
    Args:
        sale_price: Price per share at sale
        cost_base: Cost base per share (typically Price at Vesting)
        shares_sold: Number of shares sold
        long_term: Whether shares were held for > 12 months
        
    Returns:
        Tuple of (total_gain, taxable_gain)
    """
    total_gain = (sale_price - cost_base) * shares_sold
    
    if long_term and total_gain > 0:
        # Apply 50% CGT discount for assets held > 12 months
        discounted_gain = total_gain * 0.5
        return total_gain, discounted_gain
    else:
        # No discount for short-term gains or losses
        return total_gain, total_gain


def determine_financial_year(date: datetime.date) -> str:
    """
    Convert a date to Australian financial year format (e.g., '2024-25')
    
    Args:
        date: Date to convert
        
    Returns:
        Financial year string in format 'YYYY-YY'
    """
    if date.month >= 7:  # July to December
        return f"{date.year}-{date.year + 1}"
    else:  # January to June
        return f"{date.year - 1}-{date.year}"


def calculate_days_to_next_fy(date: datetime.date) -> int:
    """
    Calculate days until the next financial year starts
    
    Args:
        date: Current date
        
    Returns:
        Number of days until July 1 of next financial year
    """
    if date.month < 7:
        # Next FY starts July 1 of current year
        next_fy_start = datetime.date(date.year, 7, 1)
    else:
        # Next FY starts July 1 of next year
        next_fy_start = datetime.date(date.year + 1, 7, 1)
    
    return (next_fy_start - date).days


def is_long_term_holding(purchase_date: datetime.date, sale_date: datetime.date) -> bool:
    """
    Determine if a holding period qualifies for the 50% CGT discount
    
    Args:
        purchase_date: Date of purchase/vesting
        sale_date: Date of sale
        
    Returns:
        True if the holding period is > 12 months
    """
    # Need to hold for more than 12 months (365/366 days)
    days_held = (sale_date - purchase_date).days
    return days_held > 365


class FinancialYearTaxSummary:
    """Class to store and calculate tax summary for a financial year"""
    
    def __init__(self, year: str):
        self.financial_year = year
        self.ordinary_income = 0.0  # RSU vesting income
        self.capital_gains = 0.0    # Total capital gains
        self.cgt_discount = 0.0     # CGT discount applied
        self.net_capital_gain = 0.0  # After discount
        self.tax_withheld = 0.0     # Tax already withheld
        self.estimated_tax = 0.0    # Total estimated tax
        self.ato_item_codes = {}    # Mapping to ATO tax return items
    
    def calculate_total_income(self) -> float:
        """Calculate total taxable income"""
        return self.ordinary_income + self.net_capital_gain
    
    def calculate_tax(self, other_income: float = 0.0, has_private_health: bool = False,
                     family: bool = False, has_help_debt: bool = False) -> None:
        """Calculate tax based on income (simplified)"""
        total_income = self.calculate_total_income() + other_income
        
        # Calculate income tax only
        self.estimated_tax = calculate_income_tax(total_income, self.financial_year)
    
    def map_to_ato_items(self) -> Dict[str, float]:
        """Map financial summary data to ATO tax return item codes (simplified)"""
        self.ato_item_codes = {
            "1-Salary": self.ordinary_income,  # Item 1 on tax return
            "18-CapitalGains": self.net_capital_gain  # Item 18
        }
        return self.ato_item_codes
    
    def get_total_tax_liability(self) -> float:
        """Calculate total tax liability (simplified)"""
        return self.estimated_tax
    
    def get_remaining_tax_payable(self) -> float:
        """Calculate remaining tax after accounting for tax withheld"""
        return self.get_total_tax_liability() - self.tax_withheld


def process_vesting_data(vesting_df: pd.DataFrame, tax_rate: float) -> pd.DataFrame:
    """
    Process RSU vesting data to include tax calculations
    
    Args:
        vesting_df: DataFrame with vesting data
        tax_rate: Tax rate to apply
        
    Returns:
        Processed DataFrame with tax calculations
    """
    # Handle empty dataframe
    if vesting_df.empty:
        return vesting_df
        
    # Print column names for debugging
    print("Columns in vesting_df:", vesting_df.columns.tolist())
    
    # Standardize column names - handle both "Vested Date" and "Vesting Date"
    date_column = None
    if "Vested Date" in vesting_df.columns:
        date_column = "Vested Date"
    elif "Vesting Date" in vesting_df.columns:
        date_column = "Vesting Date"
    else:
        # If no date column found, add a default one
        vesting_df["Vesting Date"] = pd.to_datetime("today")
        date_column = "Vesting Date"
    
    # Standardize RSU column names
    rsu_column = None
    if "RSU Vested" in vesting_df.columns:
        rsu_column = "RSU Vested"
    elif "RSUs Vested" in vesting_df.columns:
        rsu_column = "RSUs Vested"
    
    # Standardize price column names
    price_column = None
    if "Price at Vesting" in vesting_df.columns:
        price_column = "Price at Vesting"
    elif "FMV at Vesting" in vesting_df.columns:
        price_column = "FMV at Vesting"
    
    # Always recalculate Gross Value if we have the necessary columns
    if rsu_column and price_column:
        # Print debug info
        print(f"Recalculating Gross Value using {rsu_column} * {price_column}")
        print(f"Sample {rsu_column} values:", vesting_df[rsu_column].head().tolist())
        print(f"Sample {price_column} values:", vesting_df[price_column].head().tolist())
        
        # Calculate Gross Value
        vesting_df["Gross Value"] = vesting_df[rsu_column] * vesting_df[price_column]
    elif "GrossValue" in vesting_df.columns:
        # Standardize column name
        vesting_df["Gross Value"] = vesting_df["GrossValue"]
    elif "Gross Value (AUD)" in vesting_df.columns:
        # Standardize column name
        vesting_df["Gross Value"] = vesting_df["Gross Value (AUD)"]
    elif "Gross Value" not in vesting_df.columns:
        # If we can't calculate it and it doesn't exist, add a default
        vesting_df["Gross Value"] = 0.0
    
    # Add Marginal Tax Rate column if it doesn't exist
    if "Marginal Tax Rate" not in vesting_df.columns:
        vesting_df["Marginal Tax Rate"] = tax_rate
    
    # Calculate tax and net value using row-specific tax rates
    vesting_df["Tax Payable"] = vesting_df.apply(
        lambda row: row["Gross Value"] * (row["Marginal Tax Rate"] / 100), axis=1
    )
    vesting_df["Net Value"] = vesting_df["Gross Value"] - vesting_df["Tax Payable"]
    
    # Print calculated values for debugging
    # print("Calculated values:")
    # print("Gross Value:", vesting_df["Gross Value"].tolist())
    # print("Tax Payable:", vesting_df["Tax Payable"].tolist())
    # print("Net Value:", vesting_df["Net Value"].tolist())
    
    # Calculate Financial Year
    vesting_df["Financial Year"] = vesting_df[date_column].apply(
        lambda x: f"{x.year}-{x.year+1}" if pd.notnull(x) and x.month >= 7 else
                 f"{x.year-1}-{x.year}" if pd.notnull(x) else "Unknown"
    )
    
    return vesting_df


def process_sales_data(sales_df: pd.DataFrame, tax_rate: float) -> pd.DataFrame:
    """
    Process RSU sales data to include capital gains calculations
    
    Args:
        sales_df: DataFrame with sales data
        tax_rate: Tax rate to apply
        
    Returns:
        Processed DataFrame with capital gains calculations
    """
    # Handle empty dataframe
    if sales_df.empty:
        return sales_df
        
    # Print column names for debugging
    print("Columns in sales_df:", sales_df.columns.tolist())
    
    # Check if Sell Date column exists
    date_column = None
    for col in sales_df.columns:
        if "date" in col.lower() or "sell" in col.lower():
            date_column = col
            break
    
    if date_column is None:
        # If no date column found, add a default one
        sales_df["Sell Date"] = pd.to_datetime("today")
        date_column = "Sell Date"
    else:
        # Ensure datetime format
        sales_df[date_column] = pd.to_datetime(sales_df[date_column], errors='coerce')
        # Rename to standard name if different
        if date_column != "Sell Date":
            sales_df["Sell Date"] = sales_df[date_column]
    
    # Standardize price column names
    price_column = None
    if "FMV at Vesting" in sales_df.columns:
        price_column = "FMV at Vesting"
    elif "Price at Vesting" in sales_df.columns:
        price_column = "Price at Vesting"
        # Rename to standard name
        sales_df["FMV at Vesting"] = sales_df[price_column]
        price_column = "FMV at Vesting"
    else:
        # If missing, add a default
        sales_df["FMV at Vesting"] = 0.0
        price_column = "FMV at Vesting"
    
    # Standardize shares column
    shares_column = None
    if "Shares Sold" in sales_df.columns:
        shares_column = "Shares Sold"
    elif "RSUs Sold" in sales_df.columns:
        shares_column = "RSUs Sold"
        # Rename to standard name
        sales_df["Shares Sold"] = sales_df[shares_column]
        shares_column = "Shares Sold"
    else:
        # If missing, add a default
        sales_df["Shares Sold"] = 0.0
        shares_column = "Shares Sold"
    
    # Standardize sale price column
    sale_price_column = None
    if "Sale Price" in sales_df.columns:
        sale_price_column = "Sale Price"
    elif "Selling Price" in sales_df.columns:
        sale_price_column = "Selling Price"
        # Rename to standard name
        sales_df["Sale Price"] = sales_df[sale_price_column]
        sale_price_column = "Sale Price"
    else:
        # If missing, add a default
        sales_df["Sale Price"] = 0.0
        sale_price_column = "Sale Price"
    
    # Check for long-term holding column
    if "Held > 12 Months" not in sales_df.columns:
        sales_df["Held > 12 Months"] = False
    
    # Calculate Gross Value (Shares Sold * Sale Price)
    sales_df["Gross Value"] = sales_df["Shares Sold"] * sales_df["Sale Price"]
    
    # Calculate capital gains
    def calculate_cgt_row(row):
        gain = (row["Sale Price"] - row["FMV at Vesting"]) * row["Shares Sold"]
        return gain * 0.5 if row["Held > 12 Months"] and gain > 0 else gain
    
    # Add Marginal Tax Rate column if it doesn't exist
    if "Marginal Tax Rate" not in sales_df.columns:
        sales_df["Marginal Tax Rate"] = tax_rate
    
    sales_df["Capital Gain"] = sales_df.apply(calculate_cgt_row, axis=1)
    
    # Calculate tax using row-specific tax rates
    sales_df["Tax on CG"] = sales_df.apply(
        lambda row: row["Capital Gain"] * (row["Marginal Tax Rate"] / 100), axis=1
    )
    sales_df["Net Proceeds"] = sales_df["Gross Value"] - sales_df["Tax on CG"]
    
    # Calculate Financial Year for sales
    sales_df["Financial Year"] = sales_df["Sell Date"].apply(
        lambda x: f"{x.year}-{x.year+1}" if pd.notnull(x) and x.month >= 7 else
                 f"{x.year-1}-{x.year}" if pd.notnull(x) else "Unknown"
    )
    
    return sales_df


def generate_financial_year_summary(
    vesting_df: pd.DataFrame, 
    sales_df: pd.DataFrame, 
    year: str,
    other_income: float = 0.0,
    has_private_health: bool = False,
    family: bool = False,
    has_help_debt: bool = False
) -> FinancialYearTaxSummary:
    """
    Generate a tax summary for a specific financial year
    
    Args:
        vesting_df: DataFrame with vesting data
        sales_df: DataFrame with sales data
        year: Financial year to summarize
        other_income: Other income to include in calculations (kept for backward compatibility)
        has_private_health: Not used in simplified version (kept for backward compatibility)
        family: Not used in simplified version (kept for backward compatibility)
        has_help_debt: Not used in simplified version (kept for backward compatibility)
        
    Returns:
        FinancialYearTaxSummary object with calculated tax information
    """
    summary = FinancialYearTaxSummary(year)
    
    # Handle empty dataframes
    if vesting_df.empty and sales_df.empty:
        summary.calculate_tax(other_income, False, False, False)  # Simplified parameters
        summary.map_to_ato_items()
        return summary
    
    try:
        # Filter data for the specified financial year
        if not vesting_df.empty and "Financial Year" in vesting_df.columns:
            year_vesting = vesting_df[vesting_df["Financial Year"] == year]
            # Calculate ordinary income from RSU vestings
            if "Gross Value" in year_vesting.columns and not year_vesting.empty:
                summary.ordinary_income = year_vesting["Gross Value"].sum()
            
            # Calculate tax withheld
            if "Tax Payable" in year_vesting.columns and not year_vesting.empty:
                summary.tax_withheld = year_vesting["Tax Payable"].sum()
        
        # Calculate capital gains
        if not sales_df.empty and "Financial Year" in sales_df.columns:
            year_sales = sales_df[sales_df["Financial Year"] == year]
            if "Capital Gain" in year_sales.columns and not year_sales.empty:
                summary.capital_gains = year_sales["Capital Gain"].sum() * 2  # Before discount
                if "Held > 12 Months" in year_sales.columns:
                    summary.cgt_discount = year_sales[year_sales["Held > 12 Months"]]["Capital Gain"].sum()
                summary.net_capital_gain = year_sales["Capital Gain"].sum()
    except Exception as e:
        print(f"Error generating financial year summary: {e}")
        # Continue with default values if there's an error
    
    # Calculate tax (simplified)
    summary.calculate_tax(other_income, False, False, False)
    
    # Map to ATO items
    summary.map_to_ato_items()
    
    return summary
