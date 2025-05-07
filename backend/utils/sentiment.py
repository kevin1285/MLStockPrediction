from dotenv import load_dotenv

from polygon import RESTClient

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from torch.nn.functional import softmax

import os

from datetime import datetime, timedelta, timezone, time
import pytz

load_dotenv()

_model = None
_tokenizer = None

def get_model_and_tokenizer():
    global _model, _tokenizer
    if _model is None or _tokenizer is None:
        print("Loading FinBERT model and tokenizer...")
        _tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
        _model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
    return _model, _tokenizer

def predict_sentiment(text):
    model, tokenizer = get_model_and_tokenizer()
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = softmax(outputs.logits, dim=-1)[0]  # convert into probabilities that sum to 1
        #print("Probabilities:", probs) # [P(neutral), P(positive), P(negative)]
    score = probs[1] - probs[2] # sentiment score = P(positive) - P(negative)
    return score.item()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
client = RESTClient(POLYGON_API_KEY)

def fetch_news_articles(ticker, start_date, end_date, max_articles=10):
    articles = []
    for n in client.list_ticker_news(
        ticker=ticker,
        published_utc_gte=start_date,
        published_utc_lt=end_date,
        limit=max_articles,
    ):
      if n.description:
        articles.append((n.description, True))
      else:
        articles.append((n.title, False))
    if not articles:
      print("no articles from " + str(start_date) + " to " + str(end_date))
    return articles

def get_news_sentiment(company_name, from_date, to_date, max_articles=15):
    articles = fetch_news_articles(company_name, from_date, to_date, max_articles)
    if len(articles) == 0:
       return 0
    weighted_sum = 0
    total_weight = 0
    for text, has_desc in articles:
       score = predict_sentiment(text)
       weight = 2 if has_desc else 1
       weighted_sum += weight * score
       total_weight += weight
    return weighted_sum / total_weight


def get_news_sentiment_today(company_name):
    eastern = pytz.timezone("US/Eastern")
    now_et = datetime.now(eastern)

    # If it's before 4:00 a.m. ET now, use yesterday's premarket
    if now_et.time() < time(4, 0):
        date_for_premarket = now_et.date() - timedelta(days=1)
    else:
        date_for_premarket = now_et.date()

    premarket_naive = datetime.combine(date_for_premarket, time(4, 0))
    premarket_dt = eastern.localize(premarket_naive).astimezone(timezone.utc)
    start_dt = premarket_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Current UTC time
    end_dt = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    print("Start:", start_dt)
    print("End:", end_dt)

    return get_news_sentiment(company_name, start_dt, end_dt)

# ------- TESTS -------------
def test_single_text_sentiment():
    print("\n=== Testing Single Text Sentiment Analysis ===")
    test_texts = [
        "The company reported strong earnings growth and exceeded market expectations.",
        "The stock price dropped significantly after the disappointing quarterly results.",
        "The company announced a new product launch that could revolutionize the market.",
        "Investors are concerned about the company's high debt levels and declining sales."
    ]
    
    for text in test_texts:
        score = predict_sentiment(text)
        print(f"\nText: {text}")
        print(f"Sentiment score: {score:.3f}")

def test_news_sentiment():
    print("\n=== Testing News Article Sentiment Analysis ===")
    # Test with a few popular stocks
    test_stocks = ['AAPL', 'TSLA', 'MSFT']
    end_dt = (datetime.utcnow()).strftime("%Y-%m-%dT%H:%M:%SZ")
    start_dt = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    for stock in test_stocks:
        print(f"\nAnalyzing news sentiment for {stock}:")
        sentiment = get_news_sentiment(stock, start_dt, end_dt)
        print(f"Average sentiment score: {sentiment:.3f}")

if __name__ == "__main__":
    print("Starting sentiment analysis tests...")
    
    # Test single text sentiment
    #test_single_text_sentiment()
    
    # Test news sentiment if API key is available
    if POLYGON_API_KEY:
        test_news_sentiment()
    else:
        print("\nSkipping news sentiment test - POLYGON_API_KEY not found in .env file")

