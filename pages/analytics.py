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
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
[data-testid="stSidebar"] { display: none !important; }
.css-1d391kg { display: none !important; }
button[data-testid*="sidebar"], button[aria-label*="sidebar"], button[title*="sidebar"], button[aria-label*="toggle"], button[title*="toggle"], [data-testid="collapsedSidebar"], [data-testid="stSidebarToggle"], [data-testid="sidebarCollapse"], [data-testid*="sidebar"] { display: none !important; }
button[style*="position: fixed"][style*="top:"] { display: none !important; }
.reportview-container .main .block-container { margin-left: 0rem !important; padding-left: 1rem !important; }
</style>
""", unsafe_allow_html=True)

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
    st.switch_page("app.py")

# -----------------------------------
# PAGE CONTENT
# -----------------------------------
# NAVBAR (title left, links center, profile right)
st.markdown("""
<style>
.top-nav { background: linear-gradient(90deg,#0b1220,#0f172a); padding:12px 20px; border-radius:8px; }
.nav-title { color: #ffffff; font-size:22px; font-weight:700; }
.nav-link { background: transparent; color: #cbd5e1; border: none; padding:6px 12px; border-radius:6px; }
.nav-link:hover { background:#111827; color:#fff; }
</style>
""", unsafe_allow_html=True)

nav1, nav2, nav3 = st.columns([2,6,1])
with nav1:
    st.markdown("<div class='nav-title'>💰 Expense Tracker</div>", unsafe_allow_html=True)
with nav2:
    st.markdown("")
with nav3:
    if "show_profile_menu" not in st.session_state:
        st.session_state.show_profile_menu = False
    if st.button("👤", key="nav_profile_top_analytics"):
        st.session_state.show_profile_menu = not st.session_state.show_profile_menu
    if st.session_state.show_profile_menu:
        menu_html = f"""
        <div id="profile-overlay" style="position:fixed; top:70px; right:24px; background:#0b1220; color:white; padding:12px; border-radius:8px; z-index:9999; box-shadow: 0 8px 24px rgba(2,6,23,0.6); min-width:150px;">
            <div style="font-weight:700; margin-bottom:8px;">{st.session_state.get('username','User')}</div>
            <a href="/dashboard" style="display:block; color:#fff; padding:8px 6px; text-decoration:none;">Dashboard</a>
            <a href="/prediction" style="display:block; color:#fff; padding:8px 6px; text-decoration:none;">Prediction</a>
            <a href="/" style="display:block; color:#fff; padding:8px 6px; text-decoration:none;">Logout</a>
        </div>
        """
        st.markdown(menu_html, unsafe_allow_html=True)

# Reserve vertical space so the profile menu can open without pushing
# the page title down (prevents layout shift when toggling menu)
st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)

st.header("📈 Expense Analytics")

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
