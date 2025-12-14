import streamlit as st
import pandas as pd
import os
import numpy as np

#Data Preparation

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))                          #outputting csv file to data folder
dataDir = os.path.join(repo_root, "data", "bls_table.csv")

def load_table():
    return pd.read_csv(dataDir, parse_dates=["date"])

dataTable = load_table()

dataTable = dataTable.rename(columns = {
    "date" : "Date",
    "unemployment_rate" : "Unemployment Rate",
    "nonfarm_payroll_employees" : "Non-Farm Payroll Employees",
    "labor_force_participation_rate_major_industry" : "Labor Force Participation Rate (Major Industry)",
    "construction_and_manufacturing" : "Construction/Manufacturing",
    "average_hourly_earnings" : "Average Hourly Earnings",
    "retail" : "Retail",
    "healthcare" : "Healthcare",
    "technology" : "Technology",
    "finance" : "Finance",
    "realEstate" : "Real Estate"
})

#Starter code
st.title("BLS Employment Dashboard")
st.markdown("Explore unemployment, payroll, and major sector employment statistics.")
st.markdown("Please Note: This data has been extracted from the most recent date that all series have released, so the current month may not be available.")

st.sidebar.subheader("Date Selection")
start_date = st.sidebar.date_input("Start Date", dataTable["Date"].min())
end_date = st.sidebar.date_input("End Date", dataTable["Date"].max())

filt_table = dataTable[(dataTable["Date"] >= pd.to_datetime(start_date)) & 
    (dataTable["Date"] <= pd.to_datetime(end_date))]

sector_col = [
    "Construction/Manufacturing",
    "Retail",
    "Healthcare",
    "Technology",
    "Finance",
    "Real Estate"
]

#Sector Selection
st.sidebar.subheader("Sector Selection")
select_sectors = st.sidebar.multiselect(
    "Choose sectors to view",
    sector_col,
    default = sector_col
)

#Table Summary
st.subheader("Employment Data")
st.dataframe(filt_table)

#KPI Summary Numbers
st.subheader("Key Performance Indicators")
latest = filt_table.iloc[-1]
previous_year = filt_table.iloc[-13] if len(filt_table) >= 13 else None
col1, col2, col3, col4 = st.columns(4)
col1.metric("Unemployment Rate", f"{latest['Unemployment Rate']:.2f}%")
col2.metric("Employement Change (Yr)", f"{latest['Unemployment Rate'] - previous_year['Unemployment Rate']:.2f} pp")
col3.metric("Average Hourly Earnings", f"${latest['Average Hourly Earnings']:.2f}")
col4.metric("Labor Force Participation", f"{latest['Labor Force Participation Rate (Major Industry)']:.2f}%")

#Unemployment Trendline
st.subheader("Unemployment Rate Over Time")
st.line_chart(filt_table.set_index("Date")["Unemployment Rate"])

#Correlation Heatmap
st.subheader("Employment Metric Correlation")
corr_cols = [
    "Unemployment Rate",
    "Average Hourly Earnings",
    "Labor Force Participation Rate (Major Industry)"
] + select_sectors
corr_map = filt_table[corr_cols].corr()
st.dataframe(
    corr_map.style.background_gradient(cmap="coolwarm").format("{:.2f}")
)

#Major Sector Trendlines
st.subheader("Comparison of Major Sectors Employment (in Thousands) Over Time")
indexed = filt_table.set_index("Date")[select_sectors]
indexed = indexed / indexed.iloc[0] * 100
st.line_chart(indexed)

#Percent Change in Series per Month
st.subheader("Monthly % Change in Sector Employment")
percent_change = filt_table.set_index("Date")[select_sectors].pct_change() * 100
percent_change = percent_change.round(2)
st.dataframe(percent_change.style.background_gradient(cmap = "RdYlGn", axis = None))

