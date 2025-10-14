import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
from datetime import datetime, timedelta
from sidebar import init_session_state, render_sidebar

# API endpoint
API_URL = "http://127.0.0.1:8000/extract"

st.set_page_config(page_title="Add Expense", layout="wide", page_icon="➕")

# Initialize session state
init_session_state()

# Render sidebar
render_sidebar()

st.title("➕ Add New Expense")
st.markdown("Upload a file or manually enter expense data")

# Create tabs
tab1, tab2, tab3 = st.tabs([
    "📁 Upload File",
    "✏️ Manual Entry",
    "✨ Generate Sample Data",
])

# ========== TAB 1 ==========
with tab1:
    st.subheader("CLASSIFY BILL with AI")
    uploaded_bills = st.file_uploader(
        "Upload bills (images)", 
        type=["png", "jpg", "jpeg", "webp"], 
        accept_multiple_files=True
    )

    if uploaded_bills:
        for f in uploaded_bills:
            with st.container(border=True):
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.image(f, width=200)

                with col2:
                    st.markdown(
                        f"""
                        <div style="font-size:16px; font-weight:600; margin-bottom:8px;">
                            📄 {f.name}
                        </div>
                        """, unsafe_allow_html=True
                    )

                    if st.button(f"🔎 Extract", key=f"extract_{f.name}", use_container_width=True):
                        files = {"file": (f.name, io.BytesIO(f.getvalue()), "image/jpeg")}
                        with st.spinner("🤖 AI loading..."):
                            resp = requests.post(API_URL, files=files)

                        if resp.ok:
                            result = resp.json()
                            st.success("✅ Extraction completed!")

                            # Thông tin hoá đơn
                            st.markdown(
                                f"""
                                <div style='padding:10px;border-radius:8px;
                                        border:2px solid #16a34a;background:#f0fdf4;'>
                                    <b>🗓 Receipt date:</b> {result['data'].get('receipt_date')}<br>
                                    <b>⏰ Upload time:</b> {result['data'].get('upload_time')}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                            # Bảng items
                            items = result['data'].get('items', [])
                            if items:
                                df = pd.DataFrame(items)
                                st.dataframe(df, use_container_width=True, hide_index=True)

                                if st.button(f"➕ Add to Expenses", key=f"add_{f.name}", type="primary", use_container_width=True):
                                    out = pd.DataFrame({
                                        "Date": [pd.to_datetime(result['data'].get("receipt_date"))]*len(df),
                                        "Category": df.get("category", pd.Series(["Other"]*len(df))),
                                        "Description": df.get("name", pd.Series([""]*len(df))),
                                        "Amount": pd.to_numeric(df.get("final_price", pd.Series([0]*len(df))), errors="coerce"),
                                    })
                                    st.session_state.uploaded_bills = [x for x in st.session_state.uploaded_bills if x["name"] != f.name]
                                    st.success("✅ Added extracted items to Expenses!")
                                    st.balloons()
                                    st.rerun()
                        else:
                            st.error(f"API error {resp.status_code}")

# ========== TAB 2 ==========
with tab2:
    st.subheader("✏️ Manual Entry")
    with st.form("manual_entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            entry_date = st.date_input("📅 Date", datetime.now())
            category = st.selectbox("🏷️ Category", ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"])
        with col2:
            amount = st.number_input("💰 Amount ($)", min_value=0.0, step=0.01, format="%.2f")
            description = st.text_input("📝 Description")
        submitted = st.form_submit_button("➕ Add Expense", type="primary", use_container_width=True)
        if submitted:
            if amount > 0:
                new_expense = pd.DataFrame({
                    'Date': [pd.to_datetime(entry_date)],
                    'Category': [category],
                    'Description': [description if description else f"{category} expense"],
                    'Amount': [amount]
                })
                st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], ignore_index=True)
                st.success(f"Added {category} expense: ${amount:.2f}")
                st.rerun()
            else:
                st.error("Please enter an amount greater than 0")

# ========== TAB 3 ==========
with tab3:
    st.subheader("✨ Generate Sample Data")
    num_records = st.number_input("Number of records", min_value=10, max_value=1000, value=200, step=10)
    date_range = st.selectbox("Date range", ["Last 30 days", "Last 3 months", "Last 6 months", "Last year"])
    if st.button("✨ Generate Sample Data", type="primary", use_container_width=True):
        np.random.seed(None)
        if date_range == "Last 30 days":
            start_date = datetime.now() - timedelta(days=30)
        elif date_range == "Last 3 months":
            start_date = datetime.now() - timedelta(days=90)
        elif date_range == "Last 6 months":
            start_date = datetime.now() - timedelta(days=180)
        else:
            start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now()
        days = (end_date - start_date).days
        mock_dates = [start_date + timedelta(days=np.random.randint(0, days)) for _ in range(num_records)]
        mock_categories = np.random.choice(["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"], size=num_records)
        mock_descriptions = [f"{cat} expense #{i}" for i, cat in enumerate(mock_categories)]
        mock_amounts = np.random.randint(20, 500, size=num_records) + np.random.random(num_records)
        mock_df = pd.DataFrame({'Date': mock_dates, 'Category': mock_categories, 'Description': mock_descriptions, 'Amount': mock_amounts})
        st.session_state.expenses = pd.concat([st.session_state.expenses, mock_df], ignore_index=True)
        st.success(f"Generated {num_records} sample records!")
        st.balloons()
        st.rerun()



