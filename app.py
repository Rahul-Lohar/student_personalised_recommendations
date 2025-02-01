# from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# import requests

# # Initialize FastAPI app
# app = FastAPI()

# # Mount static files
# app.mount("/static", StaticFiles(directory="static"), name="static")

# # Setup templates directory
# templates = Jinja2Templates(directory="templates")

# @app.get("/", response_class=HTMLResponse)
# async def get_home(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

# @app.get("/recommendations")
# async def get_recommendations():
#     """Fetch recommendations from personalised_recommendation.py API."""
#     API_URL = "http://127.0.0.1:8000/recommendations"
#     response = requests.get(API_URL)
    
#     if response.status_code == 200:
#         return response.json()
#     else:
#         return {"error": "Failed to fetch recommendations"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


from fastapi import FastAPI, Jinja2, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests
import pandas as pd
from collections import defaultdict

# API Endpoints for fetching quiz data
QUIZ_API = "https://jsonkeeper.com/b/LLQT"
SUBMISSION_API = "https://api.jsonserve.com/rJvd7g"
HISTORY_API = "https://api.jsonserve.com/XgAgFJ"

# Initialize FastAPI application
app = FastAPI()

# Set up templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

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

@app.get("/")
async def home(request: Request):
    """Render the home page with recommendations."""
    history_data = fetch_data(HISTORY_API)
    history_df = preprocess_data(history_data)
    insights = analyze_performance(history_df)
    student_category = categorize_student(insights)
    recommendations = generate_recommendations(insights)

    return templates.TemplateResponse("home.html", {
        "request": request,
        "insights": insights,
        "student_category": student_category,
        "recommendations": recommendations
    })
