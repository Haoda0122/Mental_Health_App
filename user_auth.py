import streamlit as st
import pandas as pd
import hashlib
import os

# File to store user credentials
USER_DB = "user_credentials.csv"

def load_users():
    if os.path.exists(USER_DB):
        return pd.read_csv(USER_DB)
    return pd.DataFrame(columns=["username", "password", "is_admin"])

def save_users(users_df):
    users_df.to_csv(USER_DB, index=False)

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def create_user(username, password, is_admin=False):
    users_df = load_users()
    if username in users_df["username"].values:
        return False
    hashed_pwd = hash_password(password)
    new_user = pd.DataFrame({"username": [username], "password": [hashed_pwd], "is_admin": [is_admin]})
    users_df = pd.concat([users_df, new_user], ignore_index=True)
    save_users(users_df)
    return True

def authenticate(username, password):
    users_df = load_users()
    user = users_df[users_df["username"] == username]
    if not user.empty:
        hashed_pwd = hash_password(password)
        if user["password"].values[0] == hashed_pwd:
            return True
    return False

def is_admin(username):
    users_df = load_users()
    user = users_df[users_df["username"] == username]
    if not user.empty:
        return user["is_admin"].values[0]
    return False

def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if authenticate(username, password):
            st.session_state["user"] = username
            st.session_state["is_admin"] = is_admin(username)
            st.sidebar.success(f"Logged in as {username}")
            return True
        else:
            st.sidebar.error("Invalid username or password")
    return False

def logout():
    st.session_state["user"] = None
    st.session_state["is_admin"] = False

def show_user_management():
    st.title("User Management")
    users_df = load_users()
    st.dataframe(users_df[["username", "is_admin"]])

    st.subheader("Create New User")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    is_admin = st.checkbox("Is Admin")
    if st.button("Create User"):
        if create_user(new_username, new_password, is_admin):
            st.success(f"User {new_username} created successfully")
        else:
            st.error("Username already exists")


if "user" not in st.session_state:
    st.session_state["user"] = None
    st.session_state["is_admin"] = False


if not os.path.exists(USER_DB):
    create_user("admin", "admin123", is_admin=True)
