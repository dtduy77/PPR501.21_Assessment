import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
from typing import List
import os
from dotenv import load_dotenv
from sidebar import init_session_state, render_sidebar
import requests
import json

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(page_title="Expense Tracker", layout="wide", page_icon="📊")

# Initialize session state
init_session_state()

# Category mapping from API to display names
CATEGORY_MAPPING = {
    "food": "Food",
    "coffee": "Coffee & Drinks",
    "transport": "Transport",
    "shopping": "Shopping",
    "other": "Other"
}

# Function to convert API response to DataFrame
def convert_api_data_to_dataframe(items: List[dict]) -> pd.DataFrame:
    """Convert list of ItemResponse objects to DataFrame"""
    if not items or not isinstance(items, list):
        return pd.DataFrame(columns=['Date', 'Category', 'Description', 'Amount', 'Quantity', 'UnitPrice', 'VAT'])
    
    records = []
    for item in items:
        if not isinstance(item, dict):
            st.warning(f"Skipping invalid item: {item} (expected dictionary)")
            continue
        
        # Use receipt_date if available, otherwise use upload_time, fallback to today
        date_str = item.get('receipt_date') or item.get('upload_time')
        if date_str:
            try:
                # Try parsing DD/MM/YYYY format or fallback to YYYY-MM-DD
                if '/' in date_str:
                    date = datetime.strptime(date_str, '%d/%m/%Y')
                else:
                    date = pd.to_datetime(date_str)
            except:
                date = datetime.now()
        else:
            date = datetime.now()
        
        records.append({
            'Date': date,
            'Category': CATEGORY_MAPPING.get(item.get('category', 'other'), 'Other'),
            'Description': item.get('name', 'Unknown Item'),
            'Amount': item.get('final_price') or item.get('total_price') or item.get('unit_price', 0),
            'Quantity': item.get('quantity'),
            'UnitPrice': item.get('unit_price'),
            'VAT': item.get('vat_percent')
        })
    
    return pd.DataFrame(records)

# Fetch data from API
@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_expenses_from_api(api_base_url: str, date_type: str, date: str):
    """Fetch expenses from the API"""
    try:
        response = requests.get(
            f"{api_base_url}/expenses",
            params={"type": date_type, "date": date},
            timeout=10
        )
        if response.status_code == 200:
            # Ensure the response is parsed as JSON
            data = response.json()
            if isinstance(data, dict) and 'items' in data:
                return data.get('items', [])
            return data if isinstance(data, list) else []
        else:
            st.error(f"Failed to fetch data from API: {response.status_code} - {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON response from API: {str(e)}")
        return []

# API Configuration - Load from .env file
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Title
st.title("Expense Tracker Dashboard")
st.markdown("Track and visualize your spending patterns from receipt data")

# Render sidebar
render_sidebar()

# API Filter Section
st.subheader("🔍 Data Filters")
col1, col2 = st.columns(2)

with col1:
    # Use last fetch type or default to year
    date_type = st.selectbox(
        "Query Type", 
        ["day", "month", "year"], 
        index=["day", "month", "year"].index(st.session_state.get('last_fetch_type', 'year'))
    )

with col2:
    today = datetime.now().date()
    # Use last fetch date if available and matches type, otherwise default
    if st.session_state.get('last_fetch_date'):
        try:
            last_date = datetime.strptime(st.session_state.last_fetch_date, "%Y-%m-%d").date()
            if date_type == "year" and last_date.year == today.year:
                default_date = last_date
            else:
                default_date = today
        except:
            default_date = today
    else:
        default_date = today
    
    date_input = st.date_input("Date", value=default_date)

# Check if we need to refresh data based on filter changes
needs_refresh = (
    st.session_state.get('last_fetch_type') != date_type or 
    st.session_state.get('last_fetch_date') != date_input.strftime("%Y-%m-%d") or
    st.button("🔄 Refresh Data")
)

if needs_refresh:
    # Validate date format
    try:
        selected_date = date_input.strftime("%Y-%m-%d")
    except ValueError:
        st.error("Invalid date format. Please use YYYY-MM-DD (e.g., 2025-10-14).")
        st.stop()
    
    with st.spinner(f"Fetching data for {date_type}: {selected_date}..."):
        api_data = fetch_expenses_from_api(API_BASE_URL, date_type, selected_date)
        if api_data:
            st.session_state.expenses = convert_api_data_to_dataframe(api_data)
            # Store the current filters in session state
            st.session_state.last_fetch_type = date_type
            st.session_state.last_fetch_date = selected_date
            st.success(f"Data refreshed for {date_type}: {selected_date}")
        else:
            st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Description', 'Amount', 'Quantity', 'UnitPrice', 'VAT'])
            st.warning("No data returned from API. Check your filters and API connection.")
    
    # Rerun to update the display
    st.rerun()

# Prepare data
df_all = st.session_state.expenses.copy()
df_all['Date'] = pd.to_datetime(df_all['Date'])
df_all['Year'] = df_all['Date'].dt.year
df_all['Month'] = df_all['Date'].dt.to_period('M').astype(str)
df_all['Day'] = df_all['Date'].dt.date

# Show filter info based on API filters
filter_info = [f"Type: {date_type}", f"Date: {date_input}"]
st.info(f"📌 Active Filters: {' | '.join(filter_info)} | Records: {len(df_all)}")

st.divider()

# Check if data is empty
if df_all.empty:
    st.warning("No data available. Please adjust your filter criteria.")
    st.stop()

# Key metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    total_expense = df_all['Amount'].sum()
    st.metric("💰 Total Expenses", f"{total_expense:,.3f} VND")
with col2:
    avg_expense = df_all['Amount'].mean()
    st.metric("📊 Average Transaction", f"{avg_expense:,.3f} VND")
with col3:
    st.metric("🧾 Total Transactions", len(df_all))
with col4:
    if not df_all.empty:
        top_category = df_all.groupby('Category')['Amount'].sum().idxmax()
        st.metric("🏆 Top Category", top_category)

st.divider()

st.subheader("📊 Spending Analysis")

# Create dynamic grouping based on date_type filter
if date_type == "day":
    # For daily data - show hourly or category breakdown within the day
    if not df_all.empty:
        df_all['Hour'] = df_all['Date'].dt.hour
        time_group = df_all.groupby('Hour')['Amount'].sum().reset_index()
        time_group.columns = ['Hour', 'Amount']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart: Spending by hour of day
            fig1 = px.bar(
                time_group, 
                x='Hour', 
                y='Amount',
                title=f"⏰ Spending by Hour ({date_input})",
                labels={'Hour': 'Hour of Day', 'Amount': 'Amount (VND)'},
                color='Amount',
                color_continuous_scale='Viridis'
            )
            fig1.update_layout(
                template='plotly_white',
                height=500,
                xaxis=dict(tickmode='linear', dtick=1)
            )
            plotly_config = {
                'width': 'stretch'
            }
            st.plotly_chart(fig1, config=plotly_config)
        
        with col2:
            category_data = df_all.groupby('Category')['Amount'].sum().reset_index()
            fig2 = go.Figure(data=[go.Pie(
                labels=category_data['Category'],
                values=category_data['Amount'],
                hole=0.4,
                marker=dict(line=dict(color='white', width=2))
            )])
            fig2.update_layout(
                title=f"🎯 Spending by Category",
                template='plotly_white',
                height=500
            )
            plotly_config = {
                'width': 'stretch'
            }
            st.plotly_chart(fig2, config=plotly_config)

elif date_type == "month":
    # For monthly data - show daily breakdown within the month
    if not df_all.empty:
        # Extract day from date for monthly view
        df_all['DayOfMonth'] = df_all['Date'].dt.day
        daily_monthly = df_all.groupby('DayOfMonth')['Amount'].sum().reset_index()
        daily_monthly.columns = ['Day', 'Amount']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart: Daily spending within the selected month
            fig1 = px.bar(
                daily_monthly,
                x='Day',
                y='Amount',
                title=f"📅 Daily Spending - {date_input}",
                labels={'Day': 'Day of Month', 'Amount': 'Amount (VND)'},
                color='Amount',
                color_continuous_scale='Blues'
            )
            fig1.update_layout(
                template='plotly_white',
                height=500,
                xaxis=dict(tickmode='linear', dtick=1)
            )
            plotly_config = {
                'width': 'stretch'
            }
            st.plotly_chart(fig1, config=plotly_config)
        
        with col2:
            category_data = df_all.groupby('Category')['Amount'].sum().reset_index()
            fig2 = go.Figure(data=[go.Pie(
                labels=category_data['Category'],
                values=category_data['Amount'],
                hole=0.4,
                marker=dict(line=dict(color='white', width=2))
            )])
            fig2.update_layout(
                title=f"🎯 Spending by Category",
                template='plotly_white',
                height=500
            )
            plotly_config = {
                'width': 'stretch'
            }
            st.plotly_chart(fig2, config=plotly_config)

elif date_type == "year":
    # For yearly data - show monthly breakdown within the year
    if not df_all.empty:
        monthly_yearly = df_all.groupby('Month')['Amount'].sum().reset_index()
        monthly_yearly.columns = ['Month', 'Amount']
        
        # Parse month for better display
        monthly_yearly['MonthDisplay'] = pd.to_datetime(monthly_yearly['Month'] + '-01').dt.strftime('%b %Y')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart: Monthly spending within the selected year
            fig1 = px.bar(
                monthly_yearly,
                x='MonthDisplay',
                y='Amount',
                title=f"📆 Monthly Spending - {date_input}",
                labels={'Amount': 'Amount (VND)', 'MonthDisplay': 'Month'},
                color='Amount',
                color_continuous_scale='Reds'
            )
            fig1.update_layout(
                template='plotly_white',
                height=500,
                xaxis_tickangle=45
            )
            plotly_config = {
                'width': 'stretch'
            }
            st.plotly_chart(fig1, config=plotly_config)
        
        with col2:
            category_data = df_all.groupby('Category')['Amount'].sum().reset_index()
            fig2 = go.Figure(data=[go.Pie(
                labels=category_data['Category'],
                values=category_data['Amount'],
                hole=0.4,
                marker=dict(line=dict(color='white', width=2))
            )])
            fig2.update_layout(
                title=f"🎯 Spending by Category",
                template='plotly_white',
                height=500
            )
            plotly_config = {
                'width': 'stretch'
            }
            st.plotly_chart(fig2, config=plotly_config)

# Data table with additional details
st.subheader(f"📋 Transaction Details ({len(df_all)} records)")

# Create display dataframe with more details
display_df = df_all[['Date', 'Category', 'Description', 'Quantity', 'UnitPrice', 'VAT', 'Amount']].copy()
display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
display_df['Quantity'] = display_df['Quantity'].apply(lambda x: f"{x:.0f}" if pd.notna(x) else "-")
display_df['UnitPrice'] = display_df['UnitPrice'].apply(lambda x: f"{x:.3f} VND" if pd.notna(x) else "-")
display_df['VAT'] = display_df['VAT'].apply(lambda x: f"{x:.0f}%" if pd.notna(x) else "-")
display_df['Amount'] = display_df['Amount'].apply(lambda x: f"{x:.3f} VND")

st.dataframe(
    display_df.sort_values('Date', ascending=False),
    width='stretch',
    height=400
)