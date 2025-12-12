import requests
import json
import datetime
import pandas as pd
import os
import pathlib as path
from dotenv import load_dotenv

load_dotenv() #loading API key into script
API_KEY = os.getenv("BLS_API_KEY") #api key for web scraping

url = "https://api.bls.gov/publicAPI/v2/timeseries/data/" #link to scrape
headers = {'Content-Type': 'application/json'}

start = datetime.datetime.now().year - 5 #dates to scapre web data
end = datetime.datetime.now().year

#series IDs for sections - 1
seriesID = {
    "unemployment_rate" : "LNS14000000", #unemployment rate
    "nonfarm_payroll_employees" : "CEU0000000001", #nonfarm payroll employees
    "labor_force_participation_rate_major_industry" : "LNS11300000", #labor force participation rate major industry
    "average_hourly_earnings" : "CES0500000003", #average hourly earnings
    "construction_and_manufacturing" : "CES2023610001", #construction/manufacturing         this series and below display number of employees
    "retail" : "CES4142361001", #trade/retail/wholesale/utilities            in the thousands within the table
    "healthcare" : "CES6562000001", #ambulatory, hospitals, nursing             should be able to describe fluctuations
    "technology" : "CES5000000001", #information sector - all employees            in unemployment rate with this
    "finance" : "CES5552000001", #fincial services/insurance
    "realEstate" : "CES5553000001" #real estate and rental leasing
}

def dataCollect(seriesID, start, end, API_KEY): #webscraping function -  3
    payload = {
        "seriesid": [seriesID],  
        "startyear": start,
        "endyear": end,
        "registrationkey": API_KEY
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    data = response.json()
    return data

def df_conversion(rawData, key): #converts raw data to data frame - 4
    if "Results" not in rawData:
        raise RuntimeError(f"BLS API error: {rawData}")
    jData = rawData['Results']['series'][0]['data']
    df = pd.DataFrame(jData)

    df["period"] = df["period"].str.replace("M", "").astype(int)
    df["date"] = pd.to_datetime(df["year"].astype(str) + "-" + df["period"].astype(str) + "-01")
    df[key] = pd.to_numeric(df["value"], errors = "coerce")
    return df[["date", key]]


seriesData = {} #puts webscraped data into a dictionary - 2
for key,value in seriesID.items():
    rawData = dataCollect(value, start, end, API_KEY)
    seriesData[key] = df_conversion(rawData, key)   #puts all dataframe together under key names - 5

combineData = seriesData["unemployment_rate"]
for key in seriesID:
    if key != "unemployment_rate":
        combineData = combineData.merge(seriesData[key], on = 'date', how = 'inner') #combining data frames - 7

dataFrame = combineData
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))                          #outputting csv file to data folder
dataDir = os.path.join(repo_root, "data")
os.makedirs(dataDir, exist_ok = True)
data_path = os.path.join(dataDir, "bls_table.csv")

def reference_table():
    if os.path.exists(data_path):
        return pd.read_csv(data_path, parse_dates=["date"])
    return pd.DataFrame(columns=["date"] + list(seriesID.keys()))


def table_update(newTable):
    currentTable = reference_table()
    new_data = ~newTable["date"].isin(currentTable["date"])
    if new_data.any():
        updatedTable = pd.concat([currentTable, newTable[new_data]], ignore_index = True)
        return updatedTable.sort_values("date")
    return currentTable

new_collection = combineData.copy()
updated_collection = table_update(new_collection)
updated_collection.to_csv(data_path, index = False)
