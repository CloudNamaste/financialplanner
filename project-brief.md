# Project Brief: Financial Planner - RSU Manager

## Project Overview
The Financial Planner is a Streamlit-based web application designed to help users manage their Restricted Stock Units (RSUs). It provides tools for tracking vesting schedules, managing sales, calculating tax implications, and generating reports.

## Core Requirements
1. Track RSU vesting schedules with financial calculations
2. Record and analyze RSU sales with capital gains calculations
3. Generate financial summaries by fiscal year
4. Export data to Excel and PDF formats
5. Support custom tax rate configurations
6. Provide visual representations of financial data

## Goals
- Simplify RSU financial management
- Provide accurate tax calculations for financial planning
- Enable easy tracking of RSU vesting and sales
- Generate comprehensive reports for financial decision-making

## Technical Scope
- Streamlit-based web application
- Data handling with pandas
- Excel file import/export
- PDF report generation
- Data visualization with matplotlib

## Current Status
The application has a functional prototype with three main tabs:
1. Vesting Schedule
2. RSU Sell Tracker
3. Summary

## Known Issues
- There appears to be a bug in the Financial Year calculation that required a fix (line 138-141)
- Excel files cannot be directly read by tools, limiting our ability to inspect sample data
