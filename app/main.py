import streamlit as st
import pandas as pd
from utils import load_data,filter_data, get_aqi_message
from plots import plot_aqi_trend, plot_pollutant_bar, plot_aqi_pie
import plotly.graph_objects as go

st.set_page_config(page_title="AQI Quality Explorer", layout="wide")

st.title("Air Quality Explorer-India")

df=load_data()
cities=sorted(df["City"].unique())

#sidebar filters
st.sidebar.header("Filters")
city=st.sidebar.selectbox("Select City", cities)
start=st.sidebar.date_input("Start Date",df["Date"].min().date())
end=st.sidebar.date_input("End Date",df["Date"].max().date())

filtered_df=filter_data(df,city, pd.to_datetime(start), pd.to_datetime(end))

def categorize_aqi(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"

# After filtering
filtered_df["AQI Category"] = filtered_df["AQI"].apply(categorize_aqi)

print("Available columns:", filtered_df.columns.tolist())
print(filtered_df.head())  # just to inspect the top few rows

#AQI health message
if not filtered_df.empty:
    latest_aqi=filtered_df["AQI"].iloc[-1]
    st.markdown(f"### Current AQI: **{latest_aqi: .2f}**")
    st.info(get_aqi_message(latest_aqi))

    st.plotly_chart(plot_aqi_trend(filtered_df, city), use_container_width=True)

    st.plotly_chart(plot_pollutant_bar(filtered_df), use_container_width=True)

    st.plotly_chart(plot_aqi_pie(filtered_df), use_container_width=True)
else:
    st.warning("No data available for selected city and data range.")
st.markdown("---")

#city comparison
compare=st.sidebar.checkbox("Compare with another city")
if compare:
    city2=st.sidebar.selectbox("Select Second City", [c for c in cities if c!=city])
    df2=filter_data(df,city2,pd.to_datetime(start),pd.to_datetime(end))

    st.subheader(f"AQI Comparison: {city} vs {city2}")
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['AQI'], name=city))
    fig.add_trace(go.Scatter(x=df2['Date'], y=df2['AQI'], name=city2))
    fig.update_layout(title="AQI Comparison", xaxis_title="Date", yaxis_title="AQI")
    st.plotly_chart(fig, use_container_width=True)

st.sidebar.download_button(
    label="Download Filtered CSV",
    data=filtered_df.to_csv(index=False),
    file_name=f"{city}_aqi_data.csv",
    mime="text/csv"
)