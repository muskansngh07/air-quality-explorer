import pandas as pd
import os

def load_data():
    path=os.path.join("data", "city_day.csv")
    df=pd.read_csv(path,parse_dates=["Date"])
    df.dropna(subset=["AQI"],inplace=True)
    return df

def filter_data(df,city,start_date,end_date):
    df_city=df[df["City"]==city]
    return df_city[(df_city["Date"]>=start_date) & (df_city["Date"]<=end_date)]

def get_aqi_message(aqi):
    if aqi<=50:
        return "Satisfactory Air Quality."
    elif aqi<=100:
        return "Moderate Air Quality."
    elif aqi<=200:
        return "Air Quality unhealthy for sensitive groups."
    elif aqi<=300:
        return "Air Quality unhealthy for everyone."
    elif aqi<=400:
        return "Very unhealthy with warnings of emergency conditions."
    else:
        return "Hazardous Air Quality."


