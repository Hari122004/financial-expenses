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
    layout="wide"
)

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
st.title("🤖 Expense Prediction")

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