import streamlit as st
from streamlit_extras.colored_header import colored_header
import pandas as pd
import plotly.express as px
from datetime import datetime
import user_auth
import utils
import app_components
from app_components import combined_dashboard_page

st.set_page_config(page_title="Mental Health Counselor Assistant", page_icon="🧠", layout="wide")


st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6;
    }
    .stSidebar {
        background-color: #ffffff;
        padding: 2rem;
        border-right: 1px solid #e0e0e0;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    .stSelectbox>div>div>select {
        border-radius: 5px;
    }
    .stHeader {
        background-color: #4CAF50;
        padding: 1rem;
        color: white;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .main-content {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 1rem;
        margin-top: 0;
    }
</style>
""", unsafe_allow_html=True)


st.sidebar.title("Navigation")

if not st.session_state.get("user"):
    st.image("assets/mental_health_icon.svg", width=100)
    st.title("Mental Health Counselor Assistant")
    st.write("Welcome to your personalized dashboard. Please log in to continue.")
    user_auth.login()
else:
    st.sidebar.success(f"Logged in as {st.session_state['user']}")
    if st.sidebar.button("Logout"):
        user_auth.logout()
        st.rerun()

    pages = {
        "Dashboard": "house",
        "View History": "book",
        "Feedback Stats": "bar-chart",
    }
    if st.session_state.get("is_admin"):
        pages["User Management"] = "people"

    page = st.sidebar.radio("Go to", list(pages.keys()), format_func=lambda x: f":{pages[x]}: {x}")

    st.sidebar.markdown("---")
    st.sidebar.info("👨‍⚕️ Mental Health Counselor Assistant v1.0")
    st.sidebar.markdown("© 2024 MH Assist. All rights reserved.")


    if page == "Dashboard":
        st.title("Mental Health Counselor Assistant")
        colored_header(
            label="Welcome to your personalized dashboard",
            description="Explore data, get AI-powered suggestions, and manage patient information",
            color_name="green-70"
        )
        combined_dashboard_page()

    elif page == "View History":
        colored_header(
            label="Interaction History",
            description="Review past challenges, suggestions, and provide feedback",
            color_name="blue-70"
        )
        app_components.view_history_page()

    elif page == "Feedback Stats":
        colored_header(
            label="Feedback Statistics",
            description="Analyze user feedback and system performance",
            color_name="orange-70"
        )
        app_components.feedback_stats_page()

    elif page == "User Management" and st.session_state.get("is_admin"):
        colored_header(
            label="User Management",
            description="Manage user accounts and permissions",
            color_name="red-70"
        )
        app_components.user_management_page()
