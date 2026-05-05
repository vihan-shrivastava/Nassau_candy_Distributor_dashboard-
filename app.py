import pandas as pd
import numpy as np

df=pd.read_csv(r"C:\Users\I SKY\Downloads/Nassau Candy Distributor.csv")
df['Order Date'] = pd.to_datetime(df['Order Date'], format='mixed', dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='mixed', dayfirst=True)
df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days
df = df[df['Lead Time'] >= 0]

factory_data = {
    'Factory': ['Lot\'s O\' Nuts', 'Wicked Choccy\'s', 'Sugar Shack', 'Secret Factory', 'The Other Factory'],
    'Latitude': [32.881893, 32.076176, 48.11914, 41.446333, 35.1175],
    'Longitude': [-111.768036, -81.088371, -96.18115, -90.565487, -89.971107]
}
factory_df = pd.DataFrame(factory_data)

product_factory_data = {
    'Division': ['Chocolate', 'Chocolate', 'Chocolate', 'Chocolate', 'Chocolate', 'Sugar', 'Sugar', 'Sugar', 'Sugar', 'Other', 'Sugar', 'Sugar', 'Other', 'Other', 'Other'],
    'Product Name': ['Wonka Bar - Nutty Crunch Surprise', 'Wonka Bar - Fudge Mallows', 'Wonka Bar -Scrumdiddlyumptious', 'Wonka Bar - Milk Chocolate', 'Wonka Bar - Triple Dazzle Caramel', 'Laffy Taffy', 'SweeTARTS', 'Nerds', 'Fun Dip', 'Fizzy Lifting Drinks', 'Everlasting Gobstopper', 'Hair Toffee', 'Lickable Wallpaper', 'Wonka Gum', 'Kazookles'],
    'Factory': ['Lot\'s O\' Nuts', 'Lot\'s O\' Nuts', 'Lot\'s O\' Nuts', 'Wicked Choccy\'s', 'Wicked Choccy\'s', 'Sugar Shack', 'Sugar Shack', 'Sugar Shack', 'Sugar Shack', 'Sugar Shack', 'Secret Factory', 'The Other Factory', 'Secret Factory', 'Secret Factory', 'The Other Factory']
}
product_factory_df = pd.DataFrame(product_factory_data)

df = pd.merge(df, product_factory_df, on='Product Name', how='left')
df = pd.merge(df, factory_df, on='Factory', how='left')
df['Route'] = df['Factory'] + ' to ' + df['Region']

# Normalize state-level column names for compatibility with different datasets
if 'State' not in df.columns:
    if 'State/Province' in df.columns:
        df['State'] = df['State/Province']
    else:
        raise KeyError("Expected a state column named 'State' or 'State/Province' in the dataset.")

import streamlit as st
import plotly.express as px

# -------------------------------------------------------------------------
# PRE-REQUISITES & ASSUMPTIONS
# The variable `df` is expected to be loaded before this code runs.
# We assume the following column names exist in your `df`:
# 'Order Date', 'Ship Date', 'State', 'Region', 'Ship Mode', 'Route', 
# 'Lead Time', and 'Order ID'. Modify these string keys if yours differ.
# -------------------------------------------------------------------------

st.set_page_config(page_title="Shipping Efficiency Dashboard", layout="wide")
st.title("📦 Shipping & Route Efficiency Dashboard")

# --- DATA PREPARATION ---
# Ensure dates are datetime objects for the filter
df['Order Date'] = pd.to_datetime(df['Order Date'], format='mixed', dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='mixed', dayfirst=True)

# If Lead Time doesn't exist, calculate it (Ship Date - Order Date)
if 'Lead Time' not in df.columns:
    df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days

# --- GLOBAL FILTERS (SIDEBAR) ---
st.sidebar.header("Global Filters")

# 1. Date Range Filter
min_date = df['Order Date'].min().date()
max_date = df['Order Date'].max().date()
date_selection = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Handle cases where the user hasn't selected the end date yet
if len(date_selection) == 2:
    start_date, end_date = date_selection
else:
    start_date = end_date = date_selection[0]

# 2. Region / State Selector
all_states = sorted(df['State'].dropna().unique())
selected_states = st.sidebar.multiselect(
    "Select Region / State(s)",
    options=all_states,
    default=all_states
)

# 3. Ship Mode Filter
all_modes = df['Ship Mode'].dropna().unique()
selected_modes = st.sidebar.multiselect(
    "Select Ship Mode(s)",
    options=all_modes,
    default=all_modes
)

# 4. Lead-time Threshold Slider
min_lead = int(df['Lead Time'].min())
max_lead = int(df['Lead Time'].max())
lead_threshold = st.sidebar.slider(
    "Max Lead-Time Threshold (Days)",
    min_value=min_lead,
    max_value=max_lead,
    value=max_lead
)

# --- APPLY FILTERS TO DATASET ---
mask = (
    (df['Order Date'].dt.date >= start_date) &
    (df['Order Date'].dt.date <= end_date) &
    (df['State'].isin(selected_states)) &
    (df['Ship Mode'].isin(selected_modes)) &
    (df['Lead Time'] <= lead_threshold)
)
filtered_df = df[mask]

# Stop execution if filters result in an empty dataset
if filtered_df.empty:
    st.warning("No data available with the current filter settings. Please adjust your filters.")
    st.stop()

# --- LAYOUT & SECTIONS ---

st.markdown("---")

# ==========================================
# SECTION 1: Route Efficiency Overview
# ==========================================
st.header("1. Route Efficiency Overview")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Average Lead Time by Route")
    # Aggregate data by Route
    route_avg_time = filtered_df.groupby('Route', as_index=False)['Lead Time'].mean().sort_values(by='Lead Time')
    fig_route = px.bar(
        route_avg_time.head(10), # Showing top 10 for readability
        x='Lead Time', y='Route', orientation='h',
        title="Top 10 Fastest Routes (Avg Lead Time)",
        color='Lead Time', color_continuous_scale='Viridis_r'
    )
    st.plotly_chart(fig_route, use_container_width=True)

with col2:
    st.subheader("Route Performance Leaderboard")
    # Provide a detailed table grouped by route
    leaderboard = filtered_df.groupby('Route').agg(
        Total_Orders=('Order ID', 'nunique'),
        Avg_Lead_Time=('Lead Time', 'mean'),
        Max_Lead_Time=('Lead Time', 'max')
    ).reset_index().sort_values(by='Avg_Lead_Time')
    st.dataframe(leaderboard.style.format({"Avg_Lead_Time": "{:.2f}"}), use_container_width=True, height=350)

st.markdown("---")

# ==========================================
# SECTION 2: Geographic Shipping Map
# ==========================================
st.header("2. Geographic Shipping Map")
col3, col4 = st.columns(2)

with col3:
    st.subheader("US Heatmap of Shipping Efficiency")
    # Assumes 'State' contains 2-letter US State codes (e.g., 'CA', 'TX')
    state_perf = filtered_df.groupby('State', as_index=False)['Lead Time'].mean()
    fig_map = px.choropleth(
        state_perf,
        locations='State',
        locationmode="USA-states",
        color='Lead Time',
        scope="usa",
        color_continuous_scale="RdYlGn_r", # Green is good (low time), Red is bad (high time)
        title="Average Lead Time by State"
    )
    st.plotly_chart(fig_map, use_container_width=True)

with col4:
    st.subheader("Regional Bottlenecks")
    # Highlight the top 10 states with the highest average lead time
    bottlenecks = state_perf.sort_values(by='Lead Time', ascending=False).head(10)
    fig_bottleneck = px.bar(
        bottlenecks,
        x='State', y='Lead Time',
        title="Top 10 Slowest States (Bottlenecks)",
        color='Lead Time', color_continuous_scale='Reds'
    )
    st.plotly_chart(fig_bottleneck, use_container_width=True)

st.markdown("---")

# ==========================================
# SECTION 3: Ship Mode Comparison
# ==========================================
st.header("3. Ship Mode Comparison")

st.subheader("Lead Time Distribution by Shipping Method")
# A Box plot is excellent for showing distributions and outliers across categories
fig_ship_mode = px.box(
    filtered_df,
    x='Ship Mode', y='Lead Time',
    color='Ship Mode',
    title="Lead Time Variability per Shipping Mode"
)
st.plotly_chart(fig_ship_mode, use_container_width=True)

st.markdown("---")

# ==========================================
# SECTION 4: Route Drill-Down
# ==========================================
st.header("4. Route Drill-Down")

# Allow user to pick a specific route from the filtered data for deep diving
specific_route = st.selectbox("Select a Route for Drill-Down", options=filtered_df['Route'].unique())
drill_down_df = filtered_df[filtered_df['Route'] == specific_route]

col5, col6 = st.columns([1, 2])

with col5:
    st.subheader("State-Level Insights")
    # Breakdown of performance inside this specific route by State
    state_breakdown = drill_down_df.groupby('State').agg(
        Orders=('Order ID', 'count'),
        Avg_Time=('Lead Time', 'mean')
    ).reset_index()
    st.dataframe(state_breakdown, use_container_width=True)

with col6:
    st.subheader("Order-Level Shipment Timelines")
    # Gantt chart (timeline) for individual orders on this route
    # Taking top 20 to keep the chart clean, but you can adjust this
    timeline_df = drill_down_df.head(20) 
    
    if not timeline_df.empty:
        fig_timeline = px.timeline(
            timeline_df,
            x_start="Order Date",
            x_end="Ship Date",
            y="Order ID",
            color="Ship Mode",
            title=f"Shipment Timeline for top recent orders on route: {specific_route}"
        )
        # Update y-axis to show orders from top to bottom
        fig_timeline.update_yaxes(autorange="reversed") 
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("No timeline data available for this route.")
