import streamlit as st
from streamlit_extras.card import card

def display_history_entry(entry):
    """
    Display a single history entry using a container.
    """
    with st.container():
        st.subheader(f"Challenge from {entry['timestamp']}")
        st.markdown("**Challenge:**")
        st.markdown(entry['challenge'])
        st.markdown("**Suggestions:**")
        for i, suggestion in enumerate(entry['suggestions'], 1):
            st.markdown(f"{i}. {suggestion}")
        st.markdown("---")  
