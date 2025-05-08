from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi import HTTPException

app = FastAPI()

load_dotenv()

from utils.sentiment import get_news_data_today
from utils.pap import get_trade_signal


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["*"] for all origins 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/api/analysis/{ticker}")
async def analyze_stock(ticker: str):
    try:
        trade_signal, sentiment, articles = get_trade_signal(ticker)
        return {
            "signal": trade_signal,
            "sentiment_score": sentiment,
            "articles": articles
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
