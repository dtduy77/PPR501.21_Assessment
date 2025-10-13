import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
from sidebar import init_session_state, render_sidebar

# Page configuration
st.set_page_config(page_title="Expense Tracker", layout="wide", page_icon="📊")

# Initialize session state
init_session_state()

# Title
st.title("Expense Tracker Dashboard")
st.markdown("Track and visualize your spending patterns")

# Render sidebar
render_sidebar()

# Auto generate sample data if empty
if st.session_state.expenses.empty:
    np.random.seed(42)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 10, 10)
    days = (end_date - start_date).days
    num_records = 150

    mock_dates = [start_date + timedelta(days=np.random.randint(0, days)) for _ in range(num_records)]
    mock_categories = np.random.choice(
        ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"],
        size=num_records
    )
    mock_descriptions = [f"{cat} expense #{i}" for i, cat in enumerate(mock_categories)]
    mock_amounts = np.random.randint(20, 500, size=num_records) + np.random.random(num_records)

    mock_df = pd.DataFrame({
        'Date': mock_dates,
        'Category': mock_categories,
        'Description': mock_descriptions,
        'Amount': mock_amounts
    })

    st.session_state.expenses = mock_df
    st.info("🌱 No data found — sample data generated for demo!")

# Prepare data
df_all = st.session_state.expenses.copy()
df_all['Date'] = pd.to_datetime(df_all['Date'])
df_all['Year'] = df_all['Date'].dt.year
df_all['Month'] = df_all['Date'].dt.to_period('M').astype(str)
df_all['Day'] = df_all['Date'].dt.date

# Filter Section
st.subheader("🔍 Filters")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    view_mode = st.selectbox("📊 View By", ["Daily", "Monthly", "Yearly"])

with col2:
    years = sorted(df_all['Year'].unique(), reverse=True)
    selected_year = st.selectbox("Year", ["All"] + years)

with col3:
    if selected_year != "All":
        months = sorted(df_all[df_all['Year'] == selected_year]['Month'].unique(), reverse=True)
    else:
        months = sorted(df_all['Month'].unique(), reverse=True)
    selected_month = st.selectbox("Month", ["All"] + months)

with col4:
    if selected_month != "All":
        days = sorted(df_all[df_all['Month'] == selected_month]['Day'].unique(), reverse=True)
    else:
        days = sorted(df_all['Day'].unique(), reverse=True)
    selected_day = st.selectbox("Day", ["All"] + days)

with col5:
    categories = sorted(df_all['Category'].unique())
    selected_category = st.selectbox("Category", ["All"] + categories)

# Apply filters
df = df_all.copy()
if selected_year != "All":
    df = df[df['Year'] == selected_year]
if selected_month != "All":
    df = df[df['Month'] == selected_month]
if selected_day != "All":
    df = df[df['Day'] == selected_day]
if selected_category != "All":
    df = df[df['Category'] == selected_category]

# Show filter info
filter_info = []
if selected_year != "All":
    filter_info.append(f"Year: {selected_year}")
if selected_month != "All":
    filter_info.append(f"Month: {selected_month}")
if selected_day != "All":
    filter_info.append(f"Day: {selected_day}")
if selected_category != "All":
    filter_info.append(f"Category: {selected_category}")

if filter_info:
    st.info(f"📌 Active Filters: {' | '.join(filter_info)} | Records: {len(df)}")
else:
    st.info(f"📊 Showing all data | Records: {len(df)}")

st.divider()

# Check if filtered data is empty
if df.empty:
    st.warning("⚠️ No data matches the selected filters. Please adjust your filter criteria.")
    st.stop()

# Key metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    total_expense = df['Amount'].sum()
    st.metric("💰 Total Expenses", f"${total_expense:,.2f}")
with col2:
    avg_expense = df['Amount'].mean()
    st.metric("📊 Average Transaction", f"${avg_expense:,.2f}")
with col3:
    st.metric("🧾 Total Transactions", len(df))
with col4:
    if not df.empty:
        top_category = df.groupby('Category')['Amount'].sum().idxmax()
        st.metric("🏆 Top Category", top_category)

st.divider()

# Main Charts Section
if view_mode == "Daily":
    # Daily view
    daily_data = df.groupby('Day')['Amount'].sum().reset_index()
    daily_data.columns = ['Date', 'Amount']
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=daily_data['Date'],
            y=daily_data['Amount'],
            mode='lines+markers',
            name='Daily Spending',
            fill='tozeroy',
            line=dict(color='#1f77b4', width=3),
            fillcolor='rgba(31, 119, 180, 0.3)',
            marker=dict(size=8)
        ))
        fig1.update_layout(
            title=f"📅 Daily Spending Trend ({len(daily_data)} days)",
            xaxis_title="Date",
            yaxis_title="Amount ($)",
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        category_data = df.groupby('Category')['Amount'].sum().reset_index()
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
        st.plotly_chart(fig2, use_container_width=True)

elif view_mode == "Monthly":
    # Monthly view
    monthly_data = df.groupby('Month')['Amount'].sum().reset_index()
    monthly_data.columns = ['Month', 'Amount']
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=monthly_data['Month'],
            y=monthly_data['Amount'],
            marker=dict(
                color=monthly_data['Amount'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Amount ($)")
            )
        ))
        fig1.update_layout(
            title=f"📆 Monthly Spending ({len(monthly_data)} months)",
            xaxis_title="Month",
            yaxis_title="Amount ($)",
            template='plotly_white',
            height=500
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        category_data = df.groupby('Category')['Amount'].sum().reset_index()
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
        st.plotly_chart(fig2, use_container_width=True)

else:  # Yearly
    # Yearly view
    yearly_data = df.groupby('Year')['Amount'].sum().reset_index()
    yearly_data.columns = ['Year', 'Amount']
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=yearly_data['Year'],
            y=yearly_data['Amount'],
            marker=dict(
                color=yearly_data['Amount'],
                colorscale='Plasma',
                showscale=True,
                colorbar=dict(title="Amount ($)")
            ),
            text=yearly_data['Amount'].apply(lambda x: f"${x:,.0f}"),
            textposition='outside'
        ))
        fig1.update_layout(
            title=f"🗓️ Yearly Spending ({len(yearly_data)} years)",
            xaxis_title="Year",
            yaxis_title="Amount ($)",
            template='plotly_white',
            height=500
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        category_data = df.groupby('Category')['Amount'].sum().reset_index()
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
        st.plotly_chart(fig2, use_container_width=True)

# Data table
st.subheader(f"📋 Transaction Details ({len(df)} records)")
st.dataframe(
    df[['Date', 'Category', 'Description', 'Amount']].sort_values('Date', ascending=False),
    use_container_width=True,
    height=400
)