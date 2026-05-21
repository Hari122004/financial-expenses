import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

from utils.expense_service import (
    add_expense,
    get_user_id_by_username,
    get_user_expenses,
    delete_expense,
    delete_all_user_expenses
)

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

# -----------------------------------
# CHECK LOGIN
# -----------------------------------
if "logged_in" not in st.session_state:

    st.session_state.logged_in = False

if not st.session_state.logged_in:

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

if "monthly_budget" not in st.session_state:
    st.session_state.monthly_budget = 40000

if "new_description" not in st.session_state:
    st.session_state.new_description = ""
    st.session_state.new_amount = 0.0
    st.session_state.new_date = date.today()
    st.session_state.new_category = "Food"
    st.session_state.reset_new_expense_fields = False

if st.session_state.get("reset_new_expense_fields", False):
    st.session_state.new_description = ""
    st.session_state.new_amount = 0.0
    st.session_state.new_date = date.today()
    st.session_state.new_category = "Food"
    st.session_state.reset_new_expense_fields = False

# -----------------------------------
# USERNAME
# -----------------------------------
username = st.session_state.username

# -----------------------------------
# CUSTOM CSS
# -----------------------------------
st.markdown("""
<style>

/* FULL PAGE */
.stApp {

    background: linear-gradient(
        135deg,
        #020617,
        #0f172a,
        #1e293b
    );

    color: white;
}

/* HIDE STREAMLIT */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* INPUT BOX */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stSelectbox div {

    background-color: #1e293b !important;

    color: white !important;

    border-radius: 10px !important;

    border: none !important;
}

/* BUTTON */
.stButton button {

    width: 100%;

    background-color: #2563eb;

    color: white;

    border-radius: 10px;

    height: 45px;

    border: none;

    font-size: 16px;
}

/* BUTTON HOVER */
.stButton button:hover {

    background-color: #1d4ed8;

    color: white;
}

/* TABLE */
[data-testid="stDataFrame"] {

    background-color: #111827;

    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# SIDEBAR
# -----------------------------------
st.sidebar.title("💰 Expense Tracker")

st.sidebar.success(f"Welcome {username}")

st.sidebar.page_link(
    "pages/dashboard.py",
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

# -----------------------------------
# LOGOUT
# -----------------------------------
if st.sidebar.button("🚪 Logout"):

    st.session_state.logged_in = False

    st.switch_page("app.py")

# -----------------------------------
# TITLE
# -----------------------------------
st.title("💰 Expense Tracker Dashboard")

st.write(
    "Track spending and visualize expenses instantly."
)

# -----------------------------------
# TOP SECTION
# -----------------------------------
left, right = st.columns([2,1])

# -----------------------------------
# BUDGET & METRICS
# -----------------------------------
with left:

    st.subheader("Budget Overview")

    monthly_budget = st.number_input(
        "Enter Total Monthly Budget",
        min_value=0,
        value=st.session_state.monthly_budget,
        key="monthly_budget"
    )

    data = st.session_state.expenses

    total_expense = data["Amount"].sum()

    remaining_balance = monthly_budget - total_expense
    budget_usage = total_expense / monthly_budget if monthly_budget > 0 else 0

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric("📆 Total Budget", f"₹{monthly_budget}")

    with metric2:
        st.metric("🧾 Total Expense", f"₹{total_expense}")

    with metric3:
        st.metric("💰 Remaining Budget", f"₹{remaining_balance}")

    if data.empty:
        st.info("No expenses recorded yet. Add your first expense to start tracking budgets.")
    else:
        st.write(f"**Budget usage:** {round(min(budget_usage, 1.0) * 100, 1)}%")
        st.progress(min(budget_usage, 1.0))

        if remaining_balance < 0:
            st.error("⚠️ You are over budget. Review your recent expenses and adjust your spending.")
        elif budget_usage >= 0.8:
            st.warning("⚠️ Budget is running low. Try reducing non-essential spending this month.")
        else:
            st.success("✅ Budget is on track.")

# -----------------------------------
# ADD EXPENSE
# -----------------------------------
with right:

    st.subheader("Add Expense")

    description = st.text_input(
        "Description",
        value=st.session_state.new_description,
        key="new_description"
    )

    amount = st.number_input(
        "Amount",
        min_value=0.0,
        value=st.session_state.new_amount,
        key="new_amount"
    )

    expense_date = st.date_input(
        "Date",
        value=st.session_state.new_date,
        key="new_date"
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
            "Other"].index(st.session_state.new_category) if st.session_state.new_category in ["Food","Transport","Rent","Utilities","Health","Entertainment","Education","Business","Other"] else 0,
        key="new_category"
    )

    if st.button(
        "Add Expense",
        key="add_expense_btn"
    ):

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
                st.session_state.reset_new_expense_fields = True
                st.success("Expense Added Successfully")
                st.rerun()
            else:
                st.error(f"Error: {message}")
        else:
            st.error("User not found")

# -----------------------------------
# MAIN DATA
# -----------------------------------
data = st.session_state.expenses

# -----------------------------------
# EXPENSE TABLE
# -----------------------------------
st.subheader("📋 Expenses")

if data.empty:
    st.info("No expenses added yet.")
else:
    st.dataframe(
        data,
        use_container_width=True
    )

    delete_options = [
        f"{row['expense_id']}: {row['Date']} - {row['Description']} ({row['Category']}) ₹{row['Amount']}"
        for idx, row in data.iterrows()
    ]

    with st.expander("Delete Expense"):
        selected_items = st.multiselect(
            "Choose expense(s) to delete",
            delete_options,
            key="delete_expense_selection"
        )

        if st.button("Delete Selected Expense(s)", key="delete_expense_btn"):
            if selected_items:
                user_id = get_user_id_by_username(st.session_state.username)
                for item in selected_items:
                    expense_id = item.split(":")[0]
                    delete_expense(expense_id)
                st.session_state.expenses = get_user_expenses(user_id)
                st.success("Selected expense(s) deleted.")
                st.rerun()
            else:
                st.warning("Please select at least one expense to delete.")

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
            st.rerun()

# -----------------------------------
# CHARTS
# -----------------------------------
chart1, chart2 = st.columns(2)

# -----------------------------------
# PIE CHART
# -----------------------------------
with chart1:

    st.subheader("📊 By Category")

    if not data.empty:

        pie_data = data.groupby(
            "Category"
        )["Amount"].sum().reset_index()

        fig1 = px.pie(
            pie_data,
            values="Amount",
            names="Category",
            hole=0.3
        )

        fig1.update_layout(

            paper_bgcolor="#0f172a",

            plot_bgcolor="#0f172a",

            font_color="white"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

# -----------------------------------
# BAR CHART
# -----------------------------------
with chart2:

    st.subheader("📈 Spending Over Time")

    if not data.empty:

        fig2 = px.bar(
            data,
            x="Date",
            y="Amount",
            color="Category"
        )

        fig2.update_layout(

            paper_bgcolor="#0f172a",

            plot_bgcolor="#0f172a",

            font_color="white"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )