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
tab1, tab2 = st.tabs([
    "📁 Upload File",
    "✏️ Manual Entry",
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
                            print(result)
                            # Thông tin hoá đơn
                            st.markdown(
                                    f"""
                                    <div style='padding:10px;border-radius:8px;
                                                border:2px solid var(--primary-color);
                                                background: var(--background-color-secondary);'>
                                        <span style='color: var(--text-color);'>
                                            <b>🗓 Receipt date:</b> {result['data'].get('receipt_date')}<br>
                                            <b>⏰ Upload time:</b> {result['data'].get('upload_time')}
                                        </span>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                            # Bảng items
                            items = result['data'].get('items', [])
                            if items:
                                df = pd.DataFrame(items)

                                # 👉 Nếu final_price bị thiếu hoặc toàn None thì tự tính lại
                                if "final_price" not in df or df["final_price"].isnull().all():
                                    df["quantity"] = pd.to_numeric(df.get("quantity", 0), errors="coerce").fillna(0)
                                    df["unit_price"] = pd.to_numeric(df.get("unit_price", 0), errors="coerce").fillna(0)
                                    df["vat_percent"] = pd.to_numeric(df.get("vat_percent", 0), errors="coerce").fillna(0)

                                    df["total_price"] = df["quantity"] * df["unit_price"]
                                    df["final_price"] = df["total_price"] * (1 + df["vat_percent"]/100)

                                # Hiển thị bảng
                                st.dataframe(df, use_container_width=True, hide_index=True)

                                # 👉 Tính tổng cộng
                                total_final = df["final_price"].sum()
                                st.markdown(f"### 🧾 Tổng cộng: **{total_final:,.0f} VND**")

                                # Nút add vào expenses
                                if st.button(f"➕ Add to Expenses", key=f"add_{f.name}", type="primary", use_container_width=True):
                                    out = pd.DataFrame({
                                        "Date": [pd.to_datetime(result['data'].get("receipt_date"))]*len(df),
                                        "Category": df.get("category").fillna("Other"),
                                        "Description": df.get("name").fillna(""),
                                        "Amount": pd.to_numeric(df["final_price"], errors="coerce").fillna(0),
                                    })
                                    st.session_state.uploaded_bills = [
                                        x for x in st.session_state.uploaded_bills if x["name"] != f.name
                                    ]
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
            amount = st.number_input("💰 Amount (VND)", min_value=0.0, step=0.01, format="%.3f")
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
                st.success(f"Added {category} expense: {amount:.3f} VND")
                st.rerun()
            else:
                st.error("Please enter an amount greater than 0")




