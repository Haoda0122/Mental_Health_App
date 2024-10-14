import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import dataset_utils
import data_utils
import openai_utils
import user_auth
from ml_model import predict_depression

def display_metrics():
    st.header("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Number of Patients", "1,254", delta="12%")
    
    with col2:
        st.metric("Recurring Patients Rate", "68%", delta="5%")
    
    with col3:
        st.metric("Time Effectiveness", "92%", delta="3%")
    
    with col4:
        st.metric("Patient Satisfaction", "4.8/5", delta="0.2")

def combined_dashboard_page():
    display_metrics()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Explore Dataset")
        uploaded_file = st.file_uploader("Choose a CSV or XLSX file",
                                         type=["csv", "xlsx"])
        if uploaded_file is not None:
            try:
                df = dataset_utils.load_dataset(uploaded_file)
                st.success("File uploaded successfully!")
                
                st.subheader("Quick Search")
                search_query = st.text_input("Enter search query:")
                search_column = st.selectbox("Select column to search:",
                                             df.columns)
                
                
                if search_query:
                    filtered_df = dataset_utils.search_dataset(df, search_query, search_column)
                else:
                    filtered_df = df
                
                st.dataframe(filtered_df, use_container_width=True)
                
                
                use_searched_data = st.checkbox("Use searched data in chatbot knowledge base")
                
            except Exception as e:
                st.error(f"An error occurred while processing the file: {str(e)}")
        else:
            st.info("Please upload a CSV or XLSX file to begin analysis.")
    
    with col2:
        st.subheader("Depression Prediction")
        with st.form("depression_prediction"):
            age = st.number_input("Age", min_value=18, max_value=100, value=35)
            duration = st.number_input("Duration of symptoms (weeks)", min_value=1, max_value=52, value=12)
            severity = st.selectbox("Severity", ["Mild", "Moderate", "Severe"])
            submitted = st.form_submit_button("Predict Depression")
        
        if submitted:
            prediction, probability = predict_depression(age, duration, severity)
            st.write(f"Depression Prediction: {'Yes' if prediction == 1 else 'No'}")
            st.progress(probability)
            st.write(f"Probability: {probability:.2f}")
            
            if prediction == 1:
                st.warning("This patient may be at risk for depression. Consider further evaluation.")
            else:
                st.success("This patient is not likely to be depressed based on the given information.")
    
    st.subheader("Input Your Challenge")
    with st.form("challenge_input"):
        challenge = st.text_area("Describe the challenge you're facing with a patient:", height=100)
        submitted = st.form_submit_button("Get AI Suggestions")
    
    if submitted:
        if challenge:
            with st.spinner("Generating suggestions..."):
                try:
                    context = filtered_df.to_dict('records') if use_searched_data else None
                    suggestions = openai_utils.get_suggestions(challenge, context)
                    st.success("Suggestions generated successfully!")
                    for i, suggestion in enumerate(suggestions, 1):
                        st.markdown(f"**{i}.** {suggestion}")
                    
                    data_utils.save_interaction(challenge, suggestions, st.session_state["user"])
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter a challenge before requesting suggestions.")

def view_history_page():
    history = data_utils.get_interaction_history(st.session_state["user"])
    if not history:
        st.info("No interaction history available. Start by adding some challenges!")
    else:
        for entry in history:
            with st.expander(f"Challenge from {entry['timestamp']}"):
                st.write("**Challenge:**", entry['challenge'])
                st.write("**Suggestions:**")
                for i, suggestion in enumerate(entry['suggestions'], 1):
                    st.write(f"{i}. {suggestion}")
                
                feedback_value = entry.get('feedback', '')
                if pd.isna(feedback_value):
                    feedback_value = '3'  
                elif isinstance(feedback_value, (int, float)):
                    feedback_value = str(int(feedback_value))
                elif not isinstance(feedback_value, str):
                    feedback_value = '3'  
                
                feedback = st.select_slider(
                    f"Rate the suggestions (1-5):",
                    options=["1", "2", "3", "4", "5"],
                    value=feedback_value,
                    key=f"feedback_{entry['timestamp']}"
                )
                
                if st.button("Submit Feedback", key=f"submit_{entry['timestamp']}"):
                    data_utils.save_feedback(entry['timestamp'], feedback)
                    st.success("Feedback submitted successfully!")
                    st.rerun()
        
        st.subheader("Interaction Summary")
        df = pd.DataFrame(history)
        df['suggestions'] = df['suggestions'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
        st.dataframe(df[['timestamp', 'challenge', 'suggestions', 'feedback']], use_container_width=True)

def feedback_stats_page():
    stats = data_utils.get_feedback_stats()
    
    if stats['total_interactions'] == 0:
        st.warning("No interactions recorded yet. Start by adding some challenges!")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Interactions", stats['total_interactions'])
        with col2:
            st.metric("Feedback Given", stats['feedback_given'])
        with col3:
            feedback_rate = (stats['feedback_given'] / stats['total_interactions']) * 100
            st.metric("Feedback Rate", f"{feedback_rate:.2f}%")
        
        if stats['feedback_given'] > 0:
            st.subheader("Average Rating")
            avg_rating = stats['average_rating']
            st.progress(avg_rating / 5)
            st.write(f"{avg_rating:.2f} out of 5")
            
            df = pd.read_csv("interaction_history.csv")
            feedback_counts = df['feedback'].value_counts().sort_index()
            
            if not feedback_counts.empty:
                st.subheader("Feedback Distribution")
                fig = px.bar(x=feedback_counts.index, y=feedback_counts.values, 
                             labels={'x': 'Rating', 'y': 'Count'},
                             title='Distribution of Feedback Ratings')
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("Feedback Over Time")
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['feedback'] = pd.to_numeric(df['feedback'], errors='coerce')
                df_valid = df.dropna(subset=['feedback'])
                fig_time = px.scatter(df_valid, x='timestamp', y='feedback', 
                                      title='Feedback Ratings Over Time',
                                      labels={'timestamp': 'Date', 'feedback': 'Rating'})
                fig_time.update_traces(mode='lines+markers')
                st.plotly_chart(fig_time, use_container_width=True)
            else:
                st.info("No feedback data available for visualization.")
        else:
            st.info("No feedback has been given yet. Please rate some suggestions to see statistics.")

def user_management_page():
    users_df = user_auth.load_users()
    st.dataframe(users_df[["username", "is_admin"]], use_container_width=True)

    st.subheader("Create New User")
    with st.form("create_user_form"):
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        is_admin = st.checkbox("Is Admin")
        submit_button = st.form_submit_button("Create User")

    if submit_button:
        if new_username and new_password:
            if user_auth.create_user(new_username, new_password, is_admin):
                st.success(f"User {new_username} created successfully")
            else:
                st.error("Username already exists")
        else:
            st.error("Please enter both username and password")