import streamlit as st
from pymongo.errors import DuplicateKeyError
import os
from dotenv import load_dotenv

# Load environment variables explicitly
load_dotenv()

from utils.db import DB_AVAILABLE, users_collection
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
    layout="centered"
)

# -----------------------------------
# SESSION STATE
# -----------------------------------
if "page" not in st.session_state:
    st.session_state.page = "signin"

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

/* TITLE */
.title {

    text-align: center;

    font-size: 55px;

    font-weight: bold;

    margin-bottom: 25px;

    color: #FFFFFF;
}

/* INPUT BOX */
.stTextInput input {

    background-color: #1e293b !important;

    color: white !important;

    border-radius: 10px !important;

    border: none !important;

    padding: 10px !important;

    font-size: 16px !important;
}

/* BUTTON */
.stButton button {

    width: 100%;

    background: #6a11cb;

    color: white;

    border-radius: 10px;

    height: 45px;

    font-size: 16px;

    border: none;

    margin-top: 10px;
}

/* BUTTON HOVER */
.stButton button:hover {

    background: #4e0ea5;

    color: white;
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

            stored_password = user["password"]

            if verify_password(
                password,
                stored_password
            ):

                st.success("Login Successful")

                st.session_state.logged_in = True
                st.session_state.username = user["username"]

                st.switch_page("pages/dashboard.py")

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
    option = st.radio(
        "Select Option",
        ["Sign In", "Sign Up"],
        horizontal=True,
        index=1,
        key="signup_radio"
    )

    if option == "Sign In":

        st.session_state.page = "signin"

        st.rerun()