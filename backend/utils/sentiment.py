from polygon import RESTClient
import os
import json
from datetime import datetime, timedelta, timezone, time
import pytz
import re

client = RESTClient(os.getenv("POLYGON_API_KEY"))

_model = None
def get_gemini_model():
    global _model
    if _model is None:
        print("------- GOOGLE GENAI ---------")
        import google.generativeai as genai
        print("------- LOADING PAP MODEL ---------")
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        _model = genai.GenerativeModel("gemini-1.5-flash")
        print("------- PAP MODEL LOAD DONE -------")
    return _model

def predict_sentiment(text_arr: list[str], company_name: str):
    prompt = f"""
You are a financial sentiment analyst.

Analyze each of the following news snippets for sentiment toward {company_name}. 
Give a sentiment score between -1 and 1 for each snippet. 
Avoid defaulting to neutral (0.0) unless the text truly provides no directional signal. Be more assertive in assigning clearly positive (e.g., 0.9) or negative (e.g., -0.9) scores when sentiment is implied.
Sometimes, analyzing sentiment may not be straightforward, especially when the company isn't mentioned much. 
For example, when the text describes macroeconomic, political, or geopolitical conditions (eg tariffs), your score should reflect whether those conditions favor the company.

Only return a JSON array of numbers corresponding to each snippet, without any explanation.

News snippets:
"""
    for i, text in enumerate(text_arr, 1):
        prompt += f"{i}. {text}\n"

    model = get_gemini_model()
    response = model.generate_content(
        prompt, 
        generation_config={
            "temperature": 0.0
        }
    )
    raw = response.text.strip()
    print(raw)
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    print(match)
    if match:
        raw = match.group(0)
    return json.loads(raw)

def fetch_news_articles(ticker, start_date, end_date, max_articles=10):
    articles = []
    for n in client.list_ticker_news(
        ticker=ticker,
        published_utc_gte=start_date,
        published_utc_lt=end_date,
        limit=max_articles,
    ):
        articles.append(n)
    if not articles:
      print("no articles from " + str(start_date) + " to " + str(end_date))
    return articles


def get_news_data(company_name, from_date, to_date, max_articles=15):
    articles = fetch_news_articles(company_name, from_date, to_date, max_articles)
    if len(articles) == 0:
       return 0, []
    
    text_arr = [a.description if a.description else a.title for a in articles]
    sentiment_scores = predict_sentiment(text_arr, company_name)
    
    sentiment_score_sum = 0
    processed_articles = [None] * len(articles)
    
    for i in range(len(articles)):
        a = articles[i]
        sentiment_score_sum += sentiment_scores[i]
        processed_articles[i] = {
            "url": a.article_url,
            "amp_url": a.amp_url,
            "title": a.title,
            "description": a.description,
            "author": a.author,
            "image_url": a.image_url,
            "published_utc": a.published_utc,
            "publisher": {
                "name": a.publisher.name,
                "logo_url": a.publisher.logo_url,
                "homepage_url": a.publisher.homepage_url
            },
            "tickers": a.tickers,
            "keywords": a.keywords,
            "sentiment_score": sentiment_scores[i]
        }
    avg_sentiment = sentiment_score_sum / len(articles)

    return [avg_sentiment, processed_articles]

def get_news_sentiment(company_name, from_date, to_date, max_articles=15):
    articles = fetch_news_articles(company_name, from_date, to_date, max_articles)
    if len(articles) == 0:
       return 0
    text_arr = [a.description if a.description else a.title for a in articles]
    sentiment_scores = predict_sentiment(text_arr, company_name)
    avg_sentiment = sum(sentiment_scores) / len(articles)
    return avg_sentiment


def get_news_data_today(company_name, return_articles=True):
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

    if return_articles:
        return get_news_data(company_name, start_dt, end_dt)
    else:
        return get_news_sentiment(company_name, start_dt, end_dt)


# ------- TESTS -------------
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
    test_news_sentiment()


