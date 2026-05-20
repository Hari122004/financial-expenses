import streamlit as st

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
        #0f172a,
        #111827,
        #1e293b
    );

    color: white;
}

/* HIDE STREAMLIT */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* SIDEBAR */
section[data-testid="stSidebar"] {

    background: linear-gradient(
        180deg,
        #020617,
        #0f172a
    );
}

/* SIDEBAR TEXT */
section[data-testid="stSidebar"] * {

    color: white !important;
}

/* METRIC CARD */
[data-testid="metric-container"] {

    background-color: #1e293b;

    padding: 20px;

    border-radius: 15px;

    box-shadow: 0px 3px 10px rgba(0,0,0,0.3);

    color: white;
}

/* PROFILE BUTTON */
div[data-testid="stPopover"] button {

    border-radius: 30px !important;

    background-color: #111827 !important;

    color: white !important;

    font-weight: bold !important;

    border: none !important;
}

/* TABLE */
table {

    background-color: #1e293b !important;

    color: white !important;
}

/* TEXT COLOR */
h1, h2, h3, h4, h5, h6, p, label, div {

    color: white !important;
}

/* INFO BOX */
[data-testid="stAlert"] {

    background-color: #1e293b !important;

    color: white !important;
}

/* METRIC VALUE */
[data-testid="stMetricValue"] {

    color: #38bdf8 !important;
}

/* METRIC LABEL */
[data-testid="stMetricLabel"] {

    color: #cbd5e1 !important;
}

/* SUBHEADER */
.stSubheader {

    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# SIDEBAR
# -----------------------------------
st.sidebar.title("💰 Expense Tracker")

st.sidebar.success(f"Welcome {username}")

st.sidebar.divider()

# -----------------------------------
# SIDEBAR MENU
# -----------------------------------
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
# TOP BAR
# -----------------------------------
col1, col2 = st.columns([10,2])

with col1:

    st.title("📊 Expense Tracker Dashboard")

with col2:

    with st.popover(f"👤 {username}"):

        st.markdown(f"""
        ### 👤 {username}

        Welcome to Expense Tracker
        """)

        st.divider()

        st.write("📊 Dashboard")

        st.write("➕ Add Expense")

        st.write("📈 Analytics")

        st.write("🤖 Prediction")

        st.divider()

        # -----------------------------------
        # PROFILE DETAILS
        # -----------------------------------
        st.write(f"👤 Username: {username}")

        st.write("📌 Role: User")

        st.write("✅ Status: Active")

        st.divider()

        # -----------------------------------
        # LOGOUT BUTTON
        # -----------------------------------
        if st.button(
            "🚪 Logout",
            key="logout_btn"
        ):

            st.session_state.logged_in = False

            st.session_state.page = "signin"

            st.switch_page("app.py")

# -----------------------------------
# WELCOME MESSAGE
# -----------------------------------
st.success(f"Welcome {username}")

# -----------------------------------
# METRICS
# -----------------------------------
col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "💰 Total Expense",
        "₹25,000"
    )

with col2:

    st.metric(
        "📅 Monthly Budget",
        "₹40,000"
    )

with col3:

    st.metric(
        "💵 Remaining Balance",
        "₹15,000"
    )

# -----------------------------------
# RECENT ACTIVITY
# -----------------------------------
st.subheader("📌 Recent Activity")

st.info("No recent expenses added")

# -----------------------------------
# RECENT EXPENSE TABLE
# -----------------------------------
st.subheader("📋 Recent Expenses")

expense_data = {
    "Category": [
        "Food",
        "Travel",
        "Shopping"
    ],
    "Amount": [
        "₹500",
        "₹1200",
        "₹2500"
    ],
    "Date": [
        "2026-05-10",
        "2026-05-11",
        "2026-05-12"
    ]
}

st.table(expense_data)