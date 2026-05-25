import streamlit as st
from pymongo.errors import DuplicateKeyError
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc6749.errors import OAuth2Error

# Load environment variables explicitly
load_dotenv()


def _get_config(name, default=""):
    value = os.getenv(name)
    if value:
        return value

    try:
        return st.secrets.get(name, default)
    except Exception:
        return default

GOOGLE_CLIENT_ID = _get_config("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = _get_config("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = _get_config("GOOGLE_REDIRECT_URI", "http://localhost:8501/")
GOOGLE_OAUTH_ENABLED = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)

from utils.db import DB_AVAILABLE, oauth_states_collection, users_collection
from utils.auth import (
    hash_password,
    verify_password
)

from utils.mail import send_welcome_email

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="Login Page",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide the built-in Streamlit sidebar and force the main content to use the full width.
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
# SESSION STATE
# -----------------------------------
if "page" not in st.session_state:
    st.session_state.page = "signin"


def get_google_oauth_client():
    return OAuth2Session(
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scope="openid email profile",
        redirect_uri=GOOGLE_REDIRECT_URI,
    )


def build_google_authorization_url():
    client = get_google_oauth_client()
    oauth_state = uuid.uuid4().hex
    uri, state = client.create_authorization_url(
        "https://accounts.google.com/o/oauth2/v2/auth",
        state=oauth_state,
    )
    st.session_state.google_oauth_state = state
    if DB_AVAILABLE:
        oauth_states_collection.update_one(
            {"state": state},
            {
                "$set": {
                    "state": state,
                    "action": st.session_state.get("google_oauth_action", "signin"),
                    "created_at": datetime.utcnow(),
                }
            },
            upsert=True,
        )
    return uri


def fetch_google_user_info(code):
    client = get_google_oauth_client()
    token = client.fetch_token(
        "https://oauth2.googleapis.com/token",
        code=code,
    )
    response = client.get("https://www.googleapis.com/oauth2/v3/userinfo")
    response.raise_for_status()
    return response.json()


def _get_query_param_value(query_params, key):
    value = query_params.get(key, "")
    if isinstance(value, list):
        return value[0] if value else ""
    return value


def handle_google_oauth_callback():
    query_params = st.query_params
    if not query_params:
        return

    if "error" in query_params:
        error = _get_query_param_value(query_params, "error")
        st.error(f"Google OAuth returned an error: {error}")
        st.query_params.clear()
        st.stop()

    if "code" not in query_params:
        return

    if not GOOGLE_OAUTH_ENABLED:
        st.error(
            "Google OAuth is not configured. "
            "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env."
        )
        st.query_params.clear()
        st.stop()

    state = _get_query_param_value(query_params, "state")
    oauth_record = None
    if DB_AVAILABLE:
        oauth_record = oauth_states_collection.find_one({"state": state})

    if state != st.session_state.get("google_oauth_state", "") and not oauth_record:
        st.error("Google OAuth state mismatch. Please try again.")
        st.query_params.clear()
        st.stop()

    if DB_AVAILABLE:
        oauth_record = oauth_states_collection.find_one_and_delete({"state": state})
        if not oauth_record:
            st.error("Google OAuth state mismatch. Please try again.")
            st.query_params.clear()
            st.stop()

    if oauth_record and oauth_record.get("action"):
        st.session_state.google_oauth_action = oauth_record["action"]

    code = _get_query_param_value(query_params, "code")
    try:
        user_info = fetch_google_user_info(code)
    except Exception as err:
        st.error(f"Google OAuth failed: {err}")
        st.query_params.clear()
        st.stop()

    email = user_info.get("email")
    username = user_info.get("name") or email.split("@")[0]

    if not email:
        st.error("Google account did not provide an email address.")
        st.query_params.clear()
        st.stop()

    action = st.session_state.get("google_oauth_action", "signin")
    existing_user = users_collection.find_one({"email": email})

    if action == "signup":
        if existing_user:
            st.warning("An account with this email already exists. Please sign in instead.")
        else:
            users_collection.insert_one({
                "username": username,
                "email": email,
                "password": "",
                "provider": "google"
            })
            st.success("Account created via Google. You can now sign in.")
            st.session_state.page = "signin"
    else:
        if not existing_user:
            st.warning("No account found for this Google email. Please sign up first.")
        else:
            st.success("Login Successful")
            st.session_state.logged_in = True
            st.session_state.username = existing_user["username"]
            st.session_state.page = "signin"
            st.query_params.clear()
            st.switch_page("pages/dashboard.py")

    st.query_params.clear()
    st.stop()


handle_google_oauth_callback()

# -----------------------------------
# CUSTOM CSS
# -----------------------------------
st.markdown("""
<style>
/* FULL PAGE */
.stApp {
    background: linear-gradient(135deg,#020617,#0f172a,#1e293b);
    color: white;
}

/* HIDE STREAMLIT UI chrome */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Page title styling (kept simple & robust) */
.title {
    text-align: center;
    font-size: 48px;
    font-weight: 700;
    margin-bottom: 20px;
    color: #FFFFFF;
}

/* Avoid styling internal Streamlit class names like .stTextInput or .stButton
   because they can change between Streamlit versions and break rendering
   on deployed platforms. Let Streamlit render default inputs/buttons so
   they remain visible across environments. */

</style>
""", unsafe_allow_html=True)

# Make login inputs and radio options visible with light background and dark text
st.markdown("""
<style>
.stApp input[type="text"], .stApp input[type="password"], .stApp input[type="number"], .stApp textarea {
    background-color: #f3f4f6 !important;
    color: #0f172a !important;
    border-radius: 10px !important;
    padding: 8px !important;
}

/* Make all labels white and visible */
.stApp label {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* Radio labels and option text */
.stApp [role="radiogroup"] , .stApp .stRadio {
    color: #F8FAFC !important;
}

/* Ensure placeholder text is visible */
.stApp ::placeholder { color: #0f172a !important; opacity: 0.7; }

/* Force all text divs and spans to be white for form labels */
.stApp .stTextInput label, .stApp .stNumberInput label, .stApp .stRadio label {
    color: #FFFFFF !important;
}

/* Make radio button labels (Sign In / Sign Up) visible */
.stApp [role="radiogroup"] span,
.stApp [role="radio"] span,
.stApp [role="radio"] label,
.stApp [role="radiogroup"] label,
.stApp .stRadio div,
.stApp .stRadio span {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

.stApp [role="radio"] {
    accent-color: #3b82f6 !important;
}

.stApp [role="radio"]:hover,
.stApp [role="radio"][aria-checked="false"] {
    background-color: rgba(59, 130, 246, 0.15) !important;
    border-radius: 8px !important;
    padding: 4px 8px !important;
}

/* Button styling and hover effects */
.stApp button {
    background-color: #3b82f6 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 8px 24px !important;
    transition: all 0.3s ease !important;
}

.stApp button:hover {
    background-color: #2563eb !important;
    box-shadow: 0 0 15px rgba(59, 130, 246, 0.6) !important;
    transform: translateY(-2px) !important;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# DYNAMIC TITLE
# -----------------------------------
if not DB_AVAILABLE:
    st.error(
        "Database is currently unavailable. You can still view the login page, "
        "but login/signup actions may fail until the MongoDB connection is restored."
    )

if st.session_state.page == "signin":

    st.markdown("""
    <div class="title">Login</div>
    """, unsafe_allow_html=True)

else:

    st.markdown("""
    <div class="title">Sign Up</div>
    """, unsafe_allow_html=True)

# -----------------------------------
# SIGN IN PAGE
# -----------------------------------
if st.session_state.page == "signin":

    email = st.text_input(
        "Email",
        key="signin_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="signin_password"
    )

    # -----------------------------------
    # LOGIN BUTTON
    # -----------------------------------
    if st.button("Login"):
        try:
            user = users_collection.find_one({"email": email})
        except Exception as err:
            st.error("Unable to access the database right now. Please try again later.")
            st.error(str(err))
            user = None
        if user:
            stored_password = user.get("password", "")

            if verify_password(password, stored_password):
                st.success("Login Successful")

                st.session_state.logged_in = True
                st.session_state.username = user["username"]

                st.switch_page("pages/dashboard.py")
            else:
                st.error("Incorrect password. Please try again.")
        else:
            if email:
                st.error("Email not found. Please check your email or sign up.")

    # RADIO BUTTON
    # -----------------------------------
    option = st.radio(
        "Select Option",
        ["Sign In", "Sign Up"],
        horizontal=True,
        index=0,
        key="signin_radio"
    )

    if option == "Sign Up":

        st.session_state.page = "signup"

        st.rerun()

    st.markdown("---")
    if st.button("Sign in with Google", key="google_signin"):
        if GOOGLE_OAUTH_ENABLED:
            st.session_state.google_oauth_action = "signin"
            auth_url = build_google_authorization_url()
            st.markdown(
                f'<meta http-equiv="refresh" content="0; url={auth_url}">',
                unsafe_allow_html=True
            )
            st.stop()
        else:
            st.error(
                "Google OAuth is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env."
            )

# -----------------------------------
# SIGN UP PAGE
# -----------------------------------
if st.session_state.page == "signup":

    username = st.text_input(
        "Username",
        key="signup_username"
    )

    email = st.text_input(
        "Email",
        key="signup_email"
    )

    password = st.text_input(
        "Create Password",
        type="password",
        key="signup_password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        key="confirm_password"
    )

    # -----------------------------------
    # SIGN UP BUTTON
    # -----------------------------------
    if st.button("Sign Up"):

        if password != confirm_password:

            st.error("Passwords do not match")

        else:

            hashed_pw = hash_password(password)

            try:
                users_collection.insert_one({
                    "username": username,
                    "email": email,
                    "password": hashed_pw
                })

                try:
                    send_welcome_email(email, username)
                    st.success("Account Created Successfully. A welcome email was sent.")
                except Exception as err:
                    st.success("Account Created Successfully")
                    st.warning("⚠️ Welcome email could not be sent")
                    st.error(f"**Error Details:**\n{str(err)}")
                        
                    # Show SMTP configuration status
                    smtp_configured = all([
                        os.getenv("SMTP_HOST"),
                        os.getenv("SMTP_USERNAME"),
                        os.getenv("SMTP_PASSWORD")
                    ])
                    st.info(f"**SMTP Configured:** {'✓ Yes' if smtp_configured else '✗ No'}")
                    
                    if not smtp_configured:
                        st.info("**Setup Required:**\n"
                               "1. Configure SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD in .env\n"
                               "2. For Gmail: Use an App Password (myaccount.google.com/apppasswords)\n"
                               "3. Restart the app after updating .env")

            except DuplicateKeyError:
                st.error("Email already exists")
            except Exception as err:
                st.error(f"Error creating account: {err}")

    # -----------------------------------
    # RADIO BUTTON
    # -----------------------------------
    

    if option == "Sign In":

        st.session_state.page = "signin"

        st.rerun()

    st.markdown("---")
    if st.button("Sign up with Google", key="google_signup"):
        if GOOGLE_OAUTH_ENABLED:
            st.session_state.google_oauth_action = "signup"
            auth_url = build_google_authorization_url()
            st.markdown(
                f'<meta http-equiv="refresh" content="0; url={auth_url}">',
                unsafe_allow_html=True
            )
            st.stop()
        else:
            st.error(
                "Google OAuth is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env."
            )
