import streamlit as st
import pandas as pd
import plotly.express as px

from ml_model import (
    prepare_monthly_data,
    train_and_predict,
    detect_patterns,
    predict_by_category
)
from utils.expense_service import get_user_id_by_username, get_user_expenses, delete_all_user_expenses

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Expense Prediction",
    page_icon="🤖",
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

# ============================================================
# DARK THEME
# ============================================================
st.markdown("""
<style>

.stApp{
    background-color:#020817;
    color:white;
}

h1,h2,h3,h4,h5,h6,p,label,div{
    color:white !important;
}

[data-testid="metric-container"]{
    background-color:#111827;
    border:1px solid #1e293b;
    padding:20px;
    border-radius:15px;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# TITLE
# ============================================================
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
    if st.button("👤", key="nav_profile_top_pred"):
        st.session_state.show_profile_menu = not st.session_state.show_profile_menu
    if st.session_state.show_profile_menu:
        menu_html = f"""
        <div id="profile-overlay" style="position:fixed; top:70px; right:24px; background:#0b1220; color:white; padding:12px; border-radius:8px; z-index:9999; box-shadow: 0 8px 24px rgba(2,6,23,0.6); min-width:150px;">
            <div style="font-weight:700; margin-bottom:8px;">{st.session_state.get('username','User')}</div>
            <a href="/analytics" style="display:block; color:#fff; padding:8px 6px; text-decoration:none;">Analytics</a>
            <a href="/dashboard" style="display:block; color:#fff; padding:8px 6px; text-decoration:none;">Dashboard</a>
            <a href="/" style="display:block; color:#fff; padding:8px 6px; text-decoration:none;">Logout</a>
        </div>
        """
        st.markdown(menu_html, unsafe_allow_html=True)

# Reserve vertical space so the profile menu can open without pushing
# the page title down (prevents layout shift when toggling menu)
st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)

st.header("🤖 Expense Prediction")

st.write(
    "AI-based future expense forecasting"
)

if st.button("Reset All Expenses and Predictions", key="reset_expenses_btn"):
    user_id = get_user_id_by_username(st.session_state.username)
    delete_all_user_expenses(user_id)
    st.session_state.expenses = pd.DataFrame({
        "Date": [],
        "Description": [],
        "Category": [],
        "Amount": []
    })
    st.success("All expenses reset. Prediction page will reload with cleared data.")
    st.experimental_rerun()

# ============================================================
# CHECK DATA
# ============================================================
if "expenses" not in st.session_state:
    user_id = get_user_id_by_username(st.session_state.username)
    if user_id:
        st.session_state.expenses = get_user_expenses(user_id)
    else:
        st.warning("No expense data available")
        st.stop()

if st.session_state.expenses.empty:

    st.warning(
        "No expense data available"
    )

    st.stop()

# ============================================================
# DATAFRAME
# ============================================================
data = st.session_state.expenses.copy()

# ============================================================
# CONVERT TO MODEL FORMAT
# ============================================================
expenses = []

for _, row in data.iterrows():

    expenses.append({

        "expense_date": row["Date"],

        "amount": row["Amount"],

        "category": row["Category"]
    })

# ============================================================
# PREPARE MONTHLY DATA
# ============================================================
monthly_df = prepare_monthly_data(
    expenses
)

# ============================================================
# TRAIN MODEL
# ============================================================
result = train_and_predict(
    monthly_df,
    future_months=3
)

# ============================================================
# METRICS
# ============================================================
col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Average Monthly Spend",
        f"₹{result['avg_monthly']}"
    )

with col2:

    st.metric(
        "Trend",
        result["trend"]
    )

with col3:

    st.metric(
        "Confidence",
        result["confidence"]
    )

# ============================================================
# MODEL MESSAGE
# ============================================================
st.info(result["message"])

# ============================================================
# HISTORICAL GRAPH
# ============================================================
if not monthly_df.empty:

    hist_fig = px.line(

        monthly_df,

        x="month_index",

        y="total_amount",

        markers=True,

        title="Historical Monthly Expenses",

        template="plotly_dark"
    )

    st.plotly_chart(
        hist_fig,
        use_container_width=True
    )

# ============================================================
# PREDICTION GRAPH
# ============================================================
pred_df = result["predictions"]

if not pred_df.empty:

    pred_fig = px.bar(

        pred_df,

        x="month_label",

        y="predicted_amount",

        color="predicted_amount",

        title="Predicted Future Expenses",

        template="plotly_dark"
    )

    st.plotly_chart(
        pred_fig,
        use_container_width=True
    )

# ============================================================
# PREDICTION TABLE
# ============================================================
st.subheader("📋 Future Expense Prediction")

if not pred_df.empty:

    st.dataframe(
        pred_df,
        use_container_width=True
    )

# ============================================================
# SPENDING PATTERNS
# ============================================================
patterns = detect_patterns(
    expenses
)

st.subheader("🧠 Spending Insights")

for insight in patterns["insights"]:

    st.success(insight)

# ============================================================
# CATEGORY PREDICTION
# ============================================================
category_predictions = predict_by_category(
    expenses
)

st.subheader("📊 Category Prediction")

cat_df = pd.DataFrame({

    "Category": category_predictions.keys(),

    "Predicted Amount": category_predictions.values()
})

st.dataframe(
    cat_df,
    use_container_width=True
)

# ============================================================
# CATEGORY CHART
# ============================================================
if not cat_df.empty:

    pie_fig = px.pie(

        cat_df,

        names="Category",

        values="Predicted Amount",

        title="Predicted Category Distribution",

        template="plotly_dark"
    )

    st.plotly_chart(
        pie_fig,
        use_container_width=True
    )