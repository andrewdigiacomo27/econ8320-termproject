import streamlit as st
import pandas as pd
import os

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))                          #outputting csv file to data folder
dataDir = os.path.join(repo_root, "data", "bls_table.csv")

def load_table():
    return pd.read_csv(dataDir, parse_dates=["date"])

dataTable = load_table()

st.title("BLS Employment Dashboard")
st.markdown("Explore unemployment, payroll, and sector employment statistics")

start_date = st.sidebar.date_input("Start Date", dataTable["date"].min())
end_date = st.sidebar.date_input("End Date", dataTable["date"].max())

filt_table = dataTable[(dataTable["date"] >= pd.to_datetime(start_date)) & 
    (dataTable["date"] <= pd.to_datetime(end_date))]

st.subheader("Filtered Data")
st.dataframe(filt_table)

st.subheader("Unemployment Rate Over Time")
st.line_chart(filt_table.set_index("date")["unemploymentRate"])

st.subheader("Comparison of Major Sectors to Unemployment Rate Over Time") #need to finish this
st.line