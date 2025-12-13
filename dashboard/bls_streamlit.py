import streamlit as st
import pandas as pd
import os
import numpy as np

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))                          #outputting csv file to data folder
dataDir = os.path.join(repo_root, "data", "bls_table.csv")

def load_table():
    return pd.read_csv(dataDir, parse_dates=["date"])

dataTable = load_table()

dataTable = dataTable.rename(columns = {
    "date" : "Date",
    "unemployment_rate" : "Unemployment Rate",
    "nonfarm_payroll_employees" : "Non-Farm Payroll Employees",
    "labor_force_participation_rate_major_industry" : "Labor Force Participation Rate (Major_Industry)",
    "construction_and_manufacturing" : "Construction/Manufacturing",
    "average_hourly_earnings" : "Average Hourly Earnings",
    "retail" : "Retail",
    "healthcare" : "Healthcare",
    "technology" : "Technology",
    "finance" : "Finance",
    "realEstate" : "Real Estate"
})


st.title("BLS Employment Dashboard")
st.markdown("Explore unemployment, payroll, and sector employment statistics.")
st.markdown("Data is pulled to the latest date that all series are included. Data within 4 months prior of the current month based off all pulled date.")

start_date = st.sidebar.date_input("Start Date", dataTable["Date"].min())
end_date = st.sidebar.date_input("End Date", dataTable["Date"].max())

filt_table = dataTable[(dataTable["Date"] >= pd.to_datetime(start_date)) & 
    (dataTable["Date"] <= pd.to_datetime(end_date))]

st.subheader("Filtered Data")
st.dataframe(filt_table)

st.subheader("Unemployment Rate Over Time")
st.line_chart(filt_table.set_index("Date")["Unemployment Rate"])

st.subheader("Comparison of Major Sectors Employment (in Thousands) Over Time")
sector_col = [
    "Construction/Manufacturing",
    "Retail",
    "Healthcare",
    "Technology",
    "Finance",
    "Real Estate"
]
indexed = filt_table.set_index("Date")[sector_col]
indexed = indexed / indexed.iloc[0] * 100
st.line_chart(indexed)

st.subheader("Monthly % Change in Sector Employment")
percent_change = filt_table.set_index("Date")[sector_col].pct_change() * 100
percent_change = percent_change.round(2)
st.dataframe(percent_change.style.background_gradient(cmap = "RdYlGn", axis = None))
