import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def plot_aqi_trend(df,city):
    fig=px.line(df,x="Date", y="AQI", title=f"AQI Trend in {city}")
    return fig

def plot_pollutant_bar(df):
    pollutants=["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
    avg_values=df[pollutants].mean().dropna()
    fig=px.bar(x=avg_values.index, y=avg_values.values, labels={"x": "Pollutant", "y": "Average value"},title="Average Pollutant Concentration")
    return fig

def plot_aqi_pie(df):
    if "AQI Category" not in df.columns:
        raise ValueError("Expected column 'AQI Category' not found in DataFrame.")

    pie_data = df["AQI Category"].value_counts().reset_index()
    pie_data.columns = ["Category", "Count"]

    fig = px.pie(pie_data,
                 names="Category",
                 values="Count",
                 title="AQI Category Distribution",
                 color_discrete_sequence=px.colors.qualitative.Set3)
    
    return fig


