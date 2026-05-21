import streamlit as st
import pandas as pd

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="Add Expense",
    page_icon="➕",
    layout="wide"
)

# -----------------------------------
# CHECK LOGIN
# -----------------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please Login First")
    st.switch_page("app.py")

# -----------------------------------
# SESSION STATE
# -----------------------------------
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame({
        "Date": [],
        "Description": [],
        "Category": [],
        "Amount": []
    })

# -----------------------------------
# SIDEBAR
# -----------------------------------
st.sidebar.title("💰 Expense Tracker")
st.sidebar.success(f"Welcome {st.session_state.username}")

st.sidebar.page_link(
    "pages/Dashboard.py",
    label="📊 Dashboard"
)

st.sidebar.page_link(
    "pages/add_expense.py",
    label="➕ Add Expense"
)

st.sidebar.page_link(
    "pages/analytics.py",
    label="📈 Analytics"
)

st.sidebar.page_link(
    "pages/prediction.py",
    label="🤖 Prediction"
)

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.switch_page("app.py")

# -----------------------------------
# PAGE CONTENT
# -----------------------------------
st.title("➕ Add New Expense")

with st.form("expense_form"):
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0)
    expense_date = st.date_input("Date")
    category = st.selectbox(
        "Category",
        [
            "Food",
            "Transport",
            "Rent",
            "Utilities",
            "Health",
            "Entertainment",
            "Education",
            "Business",
            "Other"
        ]
    )
    submitted = st.form_submit_button("Add Expense")

if submitted:
    new_expense = pd.DataFrame({
        "Date": [str(expense_date)],
        "Description": [description],
        "Category": [category],
        "Amount": [amount]
    })
    st.session_state.expenses = pd.concat(
        [st.session_state.expenses, new_expense],
        ignore_index=True
    )
    st.success("Expense added successfully")
    st.experimental_rerun()

st.markdown("---")

st.subheader("📋 Current Expenses")
st.dataframe(st.session_state.expenses, use_container_width=True)

if st.button("Reset All Expenses", key="reset_all_expenses_btn"):
    st.session_state.expenses = pd.DataFrame({
        "Date": [],
        "Description": [],
        "Category": [],
        "Amount": []
    })
    st.success("All expenses reset. Prediction data will update automatically.")
    st.experimental_rerun()
