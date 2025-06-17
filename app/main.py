import streamlit as st
import pandas as pd
from utils import load_data, filter_data, get_aqi_message
from plots import plot_aqi_trend, plot_pollutant_bar, plot_aqi_pie
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="AQI Quality Explorer", layout="wide")
st.title("Air Quality Explorer - India")

# Load data
df = load_data()
cities = sorted(df["City"].unique())

# Sidebar filters
st.sidebar.header("Filters")
city = st.sidebar.selectbox("Select City", cities)
start = st.sidebar.date_input("Start Date", df["Date"].min().date())
end = st.sidebar.date_input("End Date", df["Date"].max().date())

# Filter
filtered_df = filter_data(df, city, pd.to_datetime(start), pd.to_datetime(end))
clean_only = st.sidebar.checkbox("Exclude rows with missing AQI", value=True)
if clean_only:
    filtered_df = filtered_df.dropna(subset=["AQI"])

missing_count = filtered_df["AQI"].isnull().sum()
if missing_count > 0:
    st.warning(f"{missing_count} AQI values are missing in the selected range.")
    
#AQI summary
st.header(f"Air Quality Overview for {city}")
if filtered_df.empty:
    st.warning("No AQI data available for this city or date range.")
else:
    avg_aqi=filtered_df["AQI"].mean()
    most_common_category = filtered_df["AQI Category"].mode()[0]
    col1, col2=st.columns(2)
    with col1:
        st.metric("Average AQI", f"{avg_aqi:2f}")
    with col2:
        st.metric("Most Frequent Category", most_common_category)
        
# Add AQI category
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

if not filtered_df.empty:
    filtered_df["AQI Category"] = filtered_df["AQI"].apply(categorize_aqi)

    # Show latest AQI
    latest_aqi = filtered_df["AQI"].iloc[-1]
    st.markdown(f"### Current AQI: **{latest_aqi:.2f}**")
    st.info(get_aqi_message(latest_aqi))

    # AQI Trend
    st.plotly_chart(plot_aqi_trend(filtered_df, city), use_container_width=True)

    # Pollutant Distribution
    st.plotly_chart(plot_pollutant_bar(filtered_df), use_container_width=True)

    # AQI Category Pie
    st.plotly_chart(plot_aqi_pie(filtered_df), use_container_width=True)

    # Heatmap: AQI per day
    st.subheader("AQI Heatmap")
    heatmap_df = filtered_df.copy()
    heatmap_df["Day"] = heatmap_df["Date"].dt.day
    heatmap_df["Month"] = heatmap_df["Date"].dt.month_name()
    pivot = heatmap_df.pivot_table(index="Month", columns="Day", values="AQI", aggfunc="mean")

    fig_heatmap = px.imshow(
        pivot,
        labels=dict(x="Day", y="Month", color="AQI"),
        color_continuous_scale="YlOrRd",
        aspect="auto"
    )
    fig_heatmap.update_layout(title="Heatmap of AQI by Day and Month")
    st.plotly_chart(fig_heatmap, use_container_width=True)

else:
    st.warning("No data available for selected city and date range.")

st.markdown("---")

# City Comparison
compare = st.sidebar.checkbox("Compare with another city")
if compare:
    city2 = st.sidebar.selectbox("Select Second City", [c for c in cities if c != city])
    df2 = filter_data(df, city2, pd.to_datetime(start), pd.to_datetime(end))
    if clean_only:
        df2 = df2.dropna(subset=["AQI"])

    st.subheader(f"AQI Comparison: {city} vs {city2}")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['AQI'], name=city))
    fig.add_trace(go.Scatter(x=df2['Date'], y=df2['AQI'], name=city2))
    fig.update_layout(title="AQI Comparison", xaxis_title="Date", yaxis_title="AQI")
    st.plotly_chart(fig, use_container_width=True)

# Download CSV
st.sidebar.download_button(
    label="Download Filtered CSV",
    data=filtered_df.to_csv(index=False),
    file_name=f"{city}_aqi_data.csv",
    mime="text/csv"
)
