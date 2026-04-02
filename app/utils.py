import os
import pandas as pd

def get_aqi_message(aqi):
    """Categorizes AQI value based on standard breakpoints."""
    if pd.isna(aqi):
        return "Unknown"
    if aqi <= 50:
        return "Good" # Updated 'Satisfactory' to standard 'Good'
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        # Note: Standard AQI 'Unhealthy' starts here, 
        # but kept close to your logic for consistency.
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"

def load_data():
    path = os.path.join(os.path.dirname(__file__), "data", "city_day.csv")
    
    # 1. Load data
    df = pd.read_csv(path, parse_dates=["Date"])
    
    # 2. Cleanup basics
    df.dropna(subset=["City", "Date"], inplace=True)
    
    # 3. SMART FILL: Group by City so data doesn't bleed between different cities
    # This fixes the chained ffill/bfill error properly
    df["AQI"] = df.groupby("City")["AQI"].transform(lambda x: x.ffill().bfill())
    
    # 4. Handle AQI Category
    # If the CSV already has an AQI_Bucket, we use that; otherwise, we generate it
    if "AQI_Bucket" in df.columns:
        df["AQI Category"] = df["AQI_Bucket"].fillna(df["AQI"].apply(get_aqi_message))
    else:
        df["AQI Category"] = df["AQI"].apply(get_aqi_message)
        
    return df

def filter_data(df, city, start_date, end_date):
    # Ensure start_date/end_date are timestamps for comparison
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    mask = (df["City"] == city) & (df["Date"] >= start_date) & (df["Date"] <= end_date)
    return df.loc[mask]
