import streamlit as st

from utils.db import conn, cursor

from utils.auth import (
    hash_password,
    verify_password
)

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
        #6a11cb,
        #2575fc
    );
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

    background-color: white !important;

    color: black !important;

    border-radius: 10px !important;

    border: 1px solid #cccccc !important;

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

        cursor.execute("""
        SELECT * FROM users
        WHERE email=?
        """, (email,))

        user = cursor.fetchone()

        if user:

            stored_password = user[3]

            if verify_password(
                password,
                stored_password
            ):

                st.success("Login Successful")

                st.session_state.logged_in = True
                st.session_state.username = user[1]

                st.switch_page(
                    "pages/dashboard.py"
                )

            else:

                st.error("Invalid Password")

        else:

            st.error("User Not Found")

    # -----------------------------------
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

                cursor.execute("""
                INSERT INTO users(
                    username,
                    email,
                    password
                )
                VALUES (?, ?, ?)
                """, (
                    username,
                    email,
                    hashed_pw
                ))

                conn.commit()

                st.success("Account Created Successfully")

            except:

                st.error("Email already exists")

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