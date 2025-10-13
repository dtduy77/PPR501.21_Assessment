import streamlit as st
import pandas as pd

def init_session_state():
    """Initialize session state for expenses data"""
    if 'expenses' not in st.session_state:
        st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Description', 'Amount'])

def render_sidebar():
    with st.sidebar:
        st.title("📊 Expense Tracker")
        st.markdown("---")

   
        st.page_link("app.py", label="📊 Dashboard", icon="🏠")
        st.page_link("pages/add_expense.py", label="➕ Add Expense", icon="➕")


        st.markdown("---")
        st.subheader("📁 Data Management")

        if not st.session_state.expenses.empty:
            st.metric("Total Records", len(st.session_state.expenses))
            st.metric("Total Amount", f"${st.session_state.expenses['Amount'].sum():,.2f}")
            
            st.markdown("---")
            
            csv = st.session_state.expenses.to_csv(index=False)
            st.download_button("📥 Download Data", csv, "expenses.csv", "text/csv", use_container_width=True)
            
            if st.button("🗑️ Clear All Data", use_container_width=True):
                st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Description', 'Amount'])
                st.rerun()
        else:
            st.info("No data available")
