import streamlit as st
import pandas as pd
from datetime import date

from utils.expense_service import (
    add_expense,
    get_user_id_by_username,
    get_user_expenses,
    delete_all_user_expenses
)

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
    username = st.session_state.username
    user_id = get_user_id_by_username(username)
    if user_id:
        st.session_state.expenses = get_user_expenses(user_id)
    else:
        st.session_state.expenses = pd.DataFrame({
            "Date": [],
            "Description": [],
            "Category": [],
            "Amount": []
        })

if "expense_description" not in st.session_state:
    st.session_state.expense_description = ""
    st.session_state.expense_amount = 0.0
    st.session_state.expense_date = date.today()
    st.session_state.expense_category = "Food"
    st.session_state.reset_expense_fields = False

if st.session_state.get("reset_expense_fields", False):
    st.session_state.expense_description = ""
    st.session_state.expense_amount = 0.0
    st.session_state.expense_date = date.today()
    st.session_state.expense_category = "Food"
    st.session_state.reset_expense_fields = False

# -----------------------------------
# SIDEBAR
# -----------------------------------
st.sidebar.title("💰 Expense Tracker")
st.sidebar.success(f"Welcome {st.session_state.username}")

st.sidebar.page_link(
    "dashboard.py",
    label="📊 Dashboard"
)

st.sidebar.page_link(
    "add_expense.py",
    label="➕ Add Expense"
)

st.sidebar.page_link(
    "analytics.py",
    label="📈 Analytics"
)

st.sidebar.page_link(
    "prediction.py",
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
    description = st.text_input(
        "Description",
        value=st.session_state.expense_description,
        key="expense_description"
    )
    amount = st.number_input(
        "Amount",
        min_value=0.0,
        value=st.session_state.expense_amount,
        key="expense_amount"
    )
    expense_date = st.date_input(
        "Date",
        value=st.session_state.expense_date,
        key="expense_date"
    )
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
        ],
        index=["Food",
            "Transport",
            "Rent",
            "Utilities",
            "Health",
            "Entertainment",
            "Education",
            "Business",
            "Other"].index(st.session_state.expense_category) if st.session_state.expense_category in ["Food","Transport","Rent","Utilities","Health","Entertainment","Education","Business","Other"] else 0,
        key="expense_category"
    )
    submitted = st.form_submit_button("Add Expense")

if submitted:
    user_id = get_user_id_by_username(st.session_state.username)
    if user_id:
        success, message = add_expense(
            user_id,
            str(expense_date),
            description,
            category,
            amount
        )
        if success:
            st.session_state.expenses = get_user_expenses(user_id)
            st.session_state.reset_expense_fields = True
            st.success("Expense added successfully")
            st.rerun()
        else:
            st.error(f"Error: {message}")
    else:
        st.error("User not found")

st.markdown("---")

st.subheader("📋 Current Expenses")
st.dataframe(st.session_state.expenses, use_container_width=True)

if st.button("Reset All Expenses", key="reset_all_expenses_btn"):
    user_id = get_user_id_by_username(st.session_state.username)
    delete_all_user_expenses(user_id)
    st.session_state.expenses = pd.DataFrame({
        "Date": [],
        "Description": [],
        "Category": [],
        "Amount": []
    })
    st.success("All expenses reset. Prediction data will update automatically.")
    st.experimental_rerun()
