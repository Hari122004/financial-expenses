import streamlit as st
import pandas as pd
import plotly.express as px

from ml_model import detect_patterns
from utils.expense_service import get_user_id_by_username, get_user_expenses

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="Analytics",
    page_icon="📈",
    layout="wide"
)

# -----------------------------------
# CHECK LOGIN
# -----------------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please Login First")
    st.switch_page("app")

# -----------------------------------
# SESSION STATE
# -----------------------------------
if "expenses" not in st.session_state:
    user_id = get_user_id_by_username(st.session_state.username)
    if user_id:
        st.session_state.expenses = get_user_expenses(user_id)
    else:
        st.warning("No expense data available")
        st.stop()

if st.session_state.expenses.empty:
    st.warning("No expense data available")
    st.stop()

# -----------------------------------
# SIDEBAR
# -----------------------------------
st.sidebar.title("💰 Expense Tracker")
st.sidebar.success(f"Welcome {st.session_state.username}")

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

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.switch_page("app")

# -----------------------------------
# PAGE CONTENT
# -----------------------------------
st.title("📈 Expense Analytics")

data = st.session_state.expenses.copy()

total = data["Amount"].sum()
monthly_budget = st.session_state.get("monthly_budget", 0)

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Expenses", f"₹{total}")
    with col2:
        if monthly_budget > 0:
            usage_pct = round(min(total / monthly_budget, 1.0) * 100, 1)
            st.metric("Monthly Budget", f"₹{monthly_budget}", delta=f"{usage_pct}% used")

if data.empty:
    st.warning("No expenses to analyze.")
    st.stop()

if monthly_budget > 0:
    budget_usage = total / monthly_budget
    st.write(f"**Budget usage:** {round(min(budget_usage, 1.0) * 100, 1)}%")
    st.progress(min(budget_usage, 1.0))

    if budget_usage > 1:
        st.error("⚠️ Over budget: your spending exceeds the monthly limit.")
    elif budget_usage >= 0.8:
        st.warning("⚠️ Close to budget: your spending is nearing the monthly limit.")
    else:
        st.success("✅ Budget is in a healthy range.")

category_data = data.groupby("Category")["Amount"].sum().reset_index()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Category Breakdown")
    fig = px.pie(category_data, values="Amount", names="Category", hole=0.3)
    fig.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", font_color="white")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📈 Monthly Trend")
    data["Date"] = pd.to_datetime(data["Date"])
    monthly = data.groupby(pd.Grouper(key="Date", freq="ME"))["Amount"].sum().reset_index()
    monthly["Month"] = monthly["Date"].dt.strftime("%b %Y")

    budget_df = monthly.copy()
    budget_df["Budget"] = monthly_budget if monthly_budget > 0 else None
    budget_df["Savings"] = (monthly_budget - budget_df["Amount"]).round(2)

    line_fig = px.line(monthly, x="Month", y="Amount", markers=True, title="Monthly Spend")
    line_fig.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", font_color="white")
    st.plotly_chart(line_fig, use_container_width=True)

    if monthly_budget > 0:
        bar_fig = px.bar(
            budget_df,
            x="Month",
            y=["Amount", "Budget"],
            title="Monthly Spend vs Budget"
        )
        bar_fig.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", font_color="white")
        st.plotly_chart(bar_fig, use_container_width=True)

        if len(budget_df) >= 2:
            last_saved = int(budget_df.iloc[-1]["Savings"])
            prev_saved = int(budget_df.iloc[-2]["Savings"])
            last_month = budget_df.iloc[-1]["Month"]
            prev_month = budget_df.iloc[-2]["Month"]

            if last_saved < prev_saved:
                st.warning(
                    f"Alert: {last_month} savings dropped to ₹{last_saved} from ₹{prev_saved} in {prev_month}. Review your spending."
                )
            elif last_saved > prev_saved:
                st.success(
                    f"Good job! {last_month} savings increased to ₹{last_saved} from ₹{prev_saved} in {prev_month}."
                )
            else:
                st.info(
                    f"Savings in {last_month} stayed flat at ₹{last_saved} compared to {prev_month}."
                )

        st.markdown("**Monthly savings summary**")
        st.dataframe(budget_df[["Month", "Amount", "Budget", "Savings"]], use_container_width=True)

st.markdown("---")

st.subheader("🧠 Spending Patterns")

expenses = [
    {
        "expense_date": row["Date"],
        "amount": row["Amount"],
        "category": row["Category"]
    }
    for _, row in data.iterrows()
]

patterns = detect_patterns(expenses)
for insight in patterns["insights"]:
    st.success(insight)

st.markdown("---")

st.subheader("📋 Expense Table")
st.dataframe(data, use_container_width=True)
