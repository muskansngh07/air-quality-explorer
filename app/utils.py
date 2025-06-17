import os
import pandas as pd

def get_aqi_message(aqi):
    if pd.isna(aqi):
        return "Unknown"
    if aqi <= 50:
        return "Satisfactory"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 200:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 300:
        return "Unhealthy"
    elif aqi <= 400:
        return "Very Unhealthy"
    else:
        return "Hazardous"

def load_data():
    path = os.path.join(os.path.dirname(__file__), "data", "city_day.csv")
    df = pd.read_csv(path, parse_dates=["Date"])
    df.dropna(subset=["City", "Date"], inplace=True)
    df["AQI"] = df["AQI"].fillna(method="ffill").fillna(method="bfill")
    if "AQI Category" not in df.columns or df["AQI Category"].isnull().all():
        df["AQI Category"] = df["AQI"].apply(get_aqi_message)
    else:
        df["AQI Category"] = df["AQI Category"].fillna("Unknown")
    return df
