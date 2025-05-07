from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utils.sentiment import get_news_sentiment, get_news_sentiment_today


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] for all origins 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/api/analysis/{ticker}")
async def analyze_stock(ticker: str):
    sentiment_score = get_news_sentiment_today(ticker)
    return {
        "sentiment": sentiment_score
    }
