import pandas as pd
from datetime import datetime

HISTORY_FILE = "interaction_history.csv"

def save_interaction(challenge: str, suggestions: list, user: str):
    """
    Save the interaction (challenge and suggestions) to the history file.
    """
    try:
        df = pd.read_csv(HISTORY_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["timestamp", "user", "challenge", "suggestions", "feedback"])
    
    new_row = {
        "timestamp": datetime.now().isoformat(),
        "user": user,
        "challenge": challenge,
        "suggestions": "|".join(suggestions),
        "feedback": ""  
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(HISTORY_FILE, index=False)

def get_interaction_history(current_user: str):
    """
    Retrieve the interaction history from the CSV file for the current user.
    """
    try:
        df = pd.read_csv(HISTORY_FILE)
        if df.empty:
            return []
        
      
        if 'user' not in df.columns:
            df['user'] = 'Unknown'
        else:
            df['user'] = df['user'].fillna('Unknown')
        
        
        user_df = df[df['user'] == current_user]
        
        if user_df.empty:
            return []
        
        user_df["suggestions"] = user_df["suggestions"].apply(lambda x: x.split("|") if isinstance(x, str) else [])
        return user_df.to_dict("records")
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error reading interaction history: {str(e)}")
        return []

def save_feedback(timestamp: str, feedback: str):
    """
    Save user feedback for a specific interaction.
    """
    try:
        df = pd.read_csv(HISTORY_FILE)
        df.loc[df['timestamp'] == timestamp, 'feedback'] = feedback
        df.to_csv(HISTORY_FILE, index=False)
    except Exception as e:
        raise Exception(f"Error saving feedback: {str(e)}")

def get_feedback_stats():
    """
    Get statistics on user feedback.
    """
    try:
        df = pd.read_csv(HISTORY_FILE)
        total_interactions = len(df)
        feedback_given = df['feedback'].notna().sum()
        
        if feedback_given > 0:
            average_rating = df['feedback'].astype(float).mean()
        else:
            average_rating = None
        
        return {
            "total_interactions": total_interactions,
            "feedback_given": feedback_given,
            "average_rating": average_rating
        }
    except FileNotFoundError:
        return {
            "total_interactions": 0,
            "feedback_given": 0,
            "average_rating": None
        }
    except Exception as e:
        raise Exception(f"Error getting feedback stats: {str(e)}")
