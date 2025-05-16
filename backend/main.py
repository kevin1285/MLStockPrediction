from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()
import os

from utils.pap import get_pap_model, get_trade_signal
from utils.sentiment import get_gemini_model

@asynccontextmanager
async def lifespan(app):
    get_pap_model()
    get_gemini_model()
    yield

app = FastAPI(lifespan=lifespan)


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
async def analyze_stock(
    ticker: str,
    rr_ratio: float = 1.5,
    atr_sl_multiplier: float = 1.5
):
    try:
        trade_signal, sl, tp, sentiment, articles, pap_pattern = get_trade_signal(
            ticker,
            rr_ratio=rr_ratio,
            atr_sl_multiplier=atr_sl_multiplier
        )
        
        return {
            "signal": trade_signal,
            "stop_loss": sl,
            "take_profit": tp,
            "sentiment_score": sentiment,
            "articles": articles,
            "pap_pattern": pap_pattern
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

if os.getenv("AWS_EXECUTION_ENV"):
    from mangum import Mangum
    handler = Mangum(app)
    
