import os
from openai import OpenAI
import json
import streamlit as st
import pandas as pd

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def get_openai_client():
    if not OPENAI_API_KEY:
        st.error("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
        return None
    return OpenAI(api_key=OPENAI_API_KEY)

def get_recent_feedback(n=5):
    try:
        df = pd.read_csv("interaction_history.csv")
        df = df[df['feedback'] != ''].sort_values('timestamp', ascending=False).head(n)
        return df[['challenge', 'suggestions', 'feedback']].to_dict('records')
    except Exception:
        return []

def get_suggestions(challenge: str, context: list = None) -> list:
    """
    Get AI-generated suggestions for a given mental health challenge, incorporating recent feedback and optional context.
    """
    openai_client = get_openai_client()
    if not openai_client:
        return ["Error: OpenAI API key is not set."]

    recent_feedback = get_recent_feedback()
    feedback_prompt = ""
    if recent_feedback:
        feedback_prompt = "Recent feedback on previous suggestions:\n"
        for item in recent_feedback:
            feedback_prompt += f"Challenge: {item['challenge']}\n"
            feedback_prompt += f"Suggestions: {item['suggestions']}\n"
            feedback_prompt += f"Feedback: {item['feedback']}\n\n"

    context_prompt = ""
    if context:
        context_prompt = "Additional context from the dataset:\n"
        for item in context[:5]:  # Limit to first 5 items to avoid token limit
            context_prompt += json.dumps(item) + "\n"

    prompt = f"""
    As an AI assistant for mental health counselors, provide 3-5 helpful suggestions
    for addressing the following patient challenge:

    {challenge}

    {feedback_prompt}
    {context_prompt}
    Based on the recent feedback and additional context (if provided), please improve your suggestions accordingly.

    Format your response as a JSON array of strings, where each string is a suggestion.
    Ensure that your suggestions are ethical, professional, and aligned with best practices
    in mental health counseling.
    """

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("OpenAI returned an empty response.")
        
        suggestions = json.loads(content)["suggestions"]
        return suggestions
    except Exception as e:
        return [f"Error generating suggestions: {str(e)}"]
