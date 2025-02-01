# import requests
# import pandas as pd
# from fastapi import FastAPI
# from collections import defaultdict

# # API Endpoints for fetching quiz data
# QUIZ_API = "https://jsonkeeper.com/b/LLQT"
# SUBMISSION_API = "https://api.jsonserve.com/rJvd7g"
# HISTORY_API = "https://api.jsonserve.com/XgAgFJ"

# # Initialize FastAPI application
# app = FastAPI()

# def fetch_data(api_url):
#     """Retrieve data from the given API endpoint."""
#     print(f"Fetching data from {api_url}")
#     response = requests.get(api_url)
#     if response.status_code == 200:
#         return response.json()
#     print(f"Failed to fetch data from {api_url}, Status Code: {response.status_code}")
#     return {}

# def preprocess_data(history_data):
#     """Convert raw historical quiz data into a structured DataFrame."""
#     if not history_data:
#         print("No historical data received.")
#         return None
    
#     history_df = pd.DataFrame(history_data)
#     print("Raw history data:", history_df.head())
    
#     # Check if the required columns are present
#     if {'quiz_id', 'score'}.issubset(history_df.columns):
#         # Convert score to numeric values, replacing errors with 0
#         history_df['score'] = pd.to_numeric(history_df['score'], errors='coerce').fillna(0)
#         print("Processed data:\n", history_df.head())  # Log processed data
#         return history_df
#     else:
#         print("Missing required columns in historical data.")
#         print("Available columns:", history_df.columns)  # Log available columns
#         return None

# def extract_topic(quiz_data):
#     """Extract topic from quiz API response."""
#     return quiz_data.get('quiz', {}).get('topic', "Unknown")

# def extract_submission_score(submission_data):
#     """Extract and clean accuracy from submission data."""
#     accuracy = submission_data.get("accuracy", "0%")
#     try:
#         return float(accuracy.replace("%", ""))
#     except ValueError:
#         return 0

# def analyze_performance(history_df):
#     """Calculate the average score for each topic from the historical data."""
#     if history_df is None or history_df.empty:
#         print("No data available for performance analysis.")
#         return {}
    
#     topic_scores = defaultdict(list)
#     for _, row in history_df.iterrows():
#         topic_scores[row.get('quiz_id', 'Unknown')].append(row['score'])
    
#     return {topic: round(sum(scores)/len(scores), 2) for topic, scores in topic_scores.items()}

# def categorize_student(insights):
#     """Classify the student based on their average performance across topics."""
#     if not insights:
#         return "Beginner"
    
#     avg_score = sum(insights.values()) / len(insights)
    
#     if avg_score > 80:
#         return "Advanced Learner"
#     elif avg_score > 50:
#         return "Developing Learner"
#     return "Beginner"

# def generate_recommendations(insights):
#     """Provide targeted recommendations based on weak topics."""
#     if not insights:
#         return {"weak_topics": [], "advice": "No sufficient data available."}
    
#     weak_topics = [topic for topic, score in insights.items() if score < 50]
#     return {
#         "weak_topics": weak_topics,
#         "advice": "Focus on these topics and attempt more practice questions to improve."
#     }

# @app.get("/recommendations")
# def get_recommendations():
#     """API endpoint to return insights and personalized recommendations."""
#     print("Processing recommendations request...")
    
#     # Fetch historical data
#     history_data = fetch_data(HISTORY_API)
    
#     # Preprocess historical data
#     history_df = preprocess_data(history_data)
    
#     # Analyze performance based on the processed data
#     insights = analyze_performance(history_df)
    
#     # Log insights and recommendations generation
#     if insights:
#         print(f"Insights: {insights}")
#     else:
#         print("No insights available")
    
#     # Categorize the student based on performance
#     student_category = categorize_student(insights)
    
#     # Generate personalized recommendations
#     recommendations = generate_recommendations(insights)
    
#     # Return the insights, category, and recommendations
#     return {
#         "insights": insights,
#         "student_category": student_category,
#         "recommendations": recommendations
#     }

# # if __name__ == "__main__":
# #     import uvicorn
# #     uvicorn.run(app, host="0.0.0.0", port=8000)


import requests
import pandas as pd
from fastapi import FastAPI
from collections import defaultdict

# API Endpoints for fetching quiz data
QUIZ_API = "https://jsonkeeper.com/b/LLQT"
SUBMISSION_API = "https://api.jsonserve.com/rJvd7g"
HISTORY_API = "https://api.jsonserve.com/XgAgFJ"

# Initialize FastAPI application
app = FastAPI()

def fetch_data(api_url):
    """Retrieve data from the given API endpoint with error handling."""
    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return {}

def preprocess_data(history_data):
    """Convert raw historical quiz data into a structured DataFrame."""
    if not history_data:
        print("No historical data received.")
        return None
    
    history_df = pd.DataFrame(history_data)
    if {'quiz_id', 'score'}.issubset(history_df.columns):
        history_df['score'] = pd.to_numeric(history_df['score'], errors='coerce').fillna(0)
        return history_df
    else:
        print("Missing required columns in historical data.")
        return None

def analyze_performance(history_df):
    """Calculate the average score for each topic."""
    if history_df is None or history_df.empty:
        return {}
    
    topic_scores = defaultdict(list)
    for _, row in history_df.iterrows():
        topic_scores[row.get('quiz_id', 'Unknown')].append(row['score'])
    
    return {topic: round(sum(scores)/len(scores), 2) for topic, scores in topic_scores.items()}

def categorize_student(insights):
    """Classify the student based on their average performance."""
    if not insights:
        return "Beginner"
    
    avg_score = sum(insights.values()) / len(insights)
    if avg_score > 80:
        return "Advanced Learner"
    elif avg_score > 50:
        return "Developing Learner"
    return "Beginner"

def generate_recommendations(insights):
    """Provide recommendations based on weak topics."""
    if not insights:
        return {"weak_topics": [], "advice": "No sufficient data available."}
    
    weak_topics = [topic for topic, score in insights.items() if score < 50]
    return {
        "weak_topics": weak_topics,
        "advice": "Focus on these topics and attempt more practice questions."
    }

@app.get("/recommendations")
def get_recommendations():
    """API endpoint to return insights and recommendations."""
    history_data = fetch_data(HISTORY_API)
    history_df = preprocess_data(history_data)
    insights = analyze_performance(history_df)
    student_category = categorize_student(insights)
    recommendations = generate_recommendations(insights)
    
    return {
        "insights": insights,
        "student_category": student_category,
        "recommendations": recommendations
    }
