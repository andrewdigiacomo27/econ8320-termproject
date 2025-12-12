import requests
import json
import datetime
import pandas as pd
import os

API_KEY = "6f51e09102d544faa5bb235d49055a46" #api key for web scraping

url = "https://api.bls.gov/publicAPI/v2/timeseries/data/" #link to scrape
headers = {'Content-Type': 'application/json'}

start = str(datetime.datetime.now().year - 5) #dates to scapre web data
end = str(datetime.datetime.now().year)

#series IDs for sections - 1
seriesID = {
    "unemploymentRate" : "LNS14000000", #unemployment rate
    "nfPRemp" : "CEU0000000001", #nonfarm payroll employees
    "lfPRmi" : "LNS11300000", #labor force participation rate major industry
    "avgHE" : "CES0500000003", #average hourly earnings
    "construction" : "CES2023610001", #construction/manufacturing         this series and below display number of employees
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

combineData = seriesData["unemploymentRate"]
for key in ["nfPRemp", "lfPRmi", "avgHE", "construction", "retail", "healthcare", "technology", "finance", "realEstate"]:
    combineData = combineData.merge(seriesData[key], on = 'date', how = 'inner') #combining data frames - 7



dataFrame = combineData                            #outputting csv file to data folder
dataDir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.makedirs(dataDir, exist_ok = True)
data_path = os.path.join(dataDir, "bls_table.csv")
dataFrame.to_csv(data_path, index = False)