import streamlit as st
import pandas as pd
from utils import load_data, filter_data, get_aqi_message
from plots import plot_aqi_trend, plot_pollutant_bar, plot_aqi_pie
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="AQI Quality Explorer", layout="wide")
st.title("Air Quality Explorer - India")

# 1. Load data
df = load_data()
cities = sorted(df["City"].unique())

# Sidebar filters
st.sidebar.header("Filters")
city = st.sidebar.selectbox("Select City", cities)
start = st.sidebar.date_input("Start Date", df["Date"].min().date())
end = st.sidebar.date_input("End Date", df["Date"].max().date())

# 2. Filter & Clean logic
# We use pd.to_datetime to avoid comparison errors between 'date' and 'datetime64' objects
filtered_df = filter_data(df, city, pd.to_datetime(start), pd.to_datetime(end)).copy()

clean_only = st.sidebar.checkbox("Exclude rows with missing AQI", value=False)
if clean_only:
    filtered_df = filtered_df.dropna(subset=["AQI"])

if not filtered_df.empty:
    # 3. Use the categorization from utils to stay consistent
    # Your manual categorize_aqi was a duplicate of get_aqi_message in utils.py
    filtered_df["AQI Category"] = filtered_df["AQI"].apply(get_aqi_message)

    # Metrics Row
    latest_aqi = filtered_df["AQI"].iloc[-1]
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.metric("Latest AQI Reading", f"{latest_aqi:.2f}")
    with col_b:
        st.info(f"Health Status: **{get_aqi_message(latest_aqi)}**")

    # Visualizations
    st.plotly_chart(plot_aqi_trend(filtered_df, city), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_pollutant_bar(filtered_df), use_container_width=True)
    with col2:
        st.plotly_chart(plot_aqi_pie(filtered_df), use_container_width=True)
        
    # Heatmap: AQI per day
    st.subheader("AQI Heatmap")
    heatmap_df = filtered_df.copy()
    # Sort months correctly using categorical logic
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    heatmap_df["Month"] = pd.Categorical(heatmap_df["Date"].dt.month_name(), categories=month_order, ordered=True)
    heatmap_df["Day"] = heatmap_df["Date"].dt.day
    
    pivot = heatmap_df.pivot_table(index="Month", columns="Day", values="AQI", aggfunc="mean")

    fig_heatmap = px.imshow(
        pivot,
        labels=dict(x="Day", y="Month", color="AQI"),
        color_continuous_scale="YlOrRd",
        aspect="auto"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # City Comparison Sidebar Logic
    compare = st.sidebar.checkbox("Compare with another city")
    if compare:
        city2 = st.sidebar.selectbox("Select Second City", [c for c in cities if c != city])
        df2 = filter_data(df, city2, pd.to_datetime(start), pd.to_datetime(end))
        if clean_only:
            df2 = df2.dropna(subset=["AQI"])

        st.subheader(f"AQI Comparison: {city} vs {city2}")
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['AQI'], name=city))
        fig_comp.add_trace(go.Scatter(x=df2['Date'], y=df2['AQI'], name=city2))
        fig_comp.update_layout(xaxis_title="Date", yaxis_title="AQI")
        st.plotly_chart(fig_comp, use_container_width=True)

else:
    st.error("No data available for the selected range. Try expanding your dates.")

# Download CSV
st.sidebar.download_button(
    label="Download Filtered CSV",
    data=filtered_df.to_csv(index=False),
    file_name=f"{city}_aqi_data.csv",
    mime="text/csv"
)
