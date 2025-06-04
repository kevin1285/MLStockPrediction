from newsapi import NewsApiClient
from polygon import RESTClient
import os
import json
from datetime import datetime, timedelta, timezone, time
import pytz
import re
import yfinance as yf

polygon_client = RESTClient(os.getenv("POLYGON_API_KEY"))
newsapi_client = NewsApiClient(os.getenv("NEWSAPI_API_KEY"))

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

def predict_sentiment(text_arr: list[str], ticker: str):
    prompt = f"""
You are a financial sentiment analyst.

Analyze each of the following news snippets for sentiment toward {ticker}. 
Give a sentiment score between -1 and 1 for each snippet, based off whether the news content is good or bad for the stock price of the company.
Avoid defaulting to neutral (0.0) unless the text truly provides no directional signal. Be more assertive in assigning clearly positive (e.g., 0.9) or negative (e.g., -0.9) scores when sentiment is implied.
Sometimes, analyzing sentiment may not be straightforward, especially when the company isn't mentioned much. 
For example, when the text describes macroeconomic, political, or geopolitical conditions, your score should reflect whether those conditions favor the company. Here are some examples of positive and negative conditions for the company:
positive:
- low interest rates
- favorable industry trends (e.g., EV adoption, AI investment)
- war or increased defense spending (if the company produces military equipment)
- tax cuts or relaxed regulations
negative:
- tariffs related to the company's operations
- government discouragement of foreign production (e.g., Trump wanting Apple )
- geopolitical conflict that could disrupt trade or supply chains
- recession
- rising interest rates or high Treasury yields (higher borrowing costs, valuation compression)
- positive things about competitors


Only return a JSON array of numbers corresponding to each snippet, without any explanation.

News snippets:
"""
    for i, text in enumerate(text_arr, 1):
        prompt += f"{i}. {text}\n"

    model = get_gemini_model()
    response = model.generate_content(
        prompt, 
        generation_config={
            "temperature": 0.0 # ensures no variability
        }
    )
    raw = response.text.strip()
    print(raw)
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    print(match)
    if match:
        raw = match.group(0)
    return json.loads(raw)

def fetch_polygon_articles(ticker, start_date, end_date, max_articles=10):
    articles = []
    for n in polygon_client.list_ticker_news(
        ticker=ticker,
        published_utc_gte=start_date,
        published_utc_lt=end_date,
        limit=max_articles,
        sort="published_utc",
        order="desc"
    ):
        articles.append(n)
    if not articles:
      print("no articles from " + str(start_date) + " to " + str(end_date))
    articles = [a for a in articles if a.description]
    return articles

def fetch_newsapi_articles(ticker, start_date, end_date, max_articles=7):
    def to_newsapi_datetime(dt_str):
        return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%dT%H:%M:%S")

    start_date = to_newsapi_datetime(start_date)
    end_date = to_newsapi_datetime(end_date)

    info = yf.Ticker(ticker).info
    company_name = info.get("shortName", info.get("longName"))
    print(f"Fetching newsapi for {ticker} ({company_name}) from {start_date} to {end_date}")

    try:
        data = newsapi_client.get_everything(
            q=f"{ticker} OR {company_name}",
            from_param=start_date,
            to=end_date,
            language='en',
            page_size=max_articles,  
            page=1,
            sort_by="popularity",
            exclude_domains="biztoc.com,globenewswire.com,rlsbb.cc"
        )
        print(data.get("message"))
    except Exception as e:
        print("Exception in fetching newsapi: ", e)
        return []
    print(data)
    articles = data.get("articles")
    if not articles:
        print("no articles from " + str(start_date) + " to " + str(end_date))
    articles = [a for a in articles if a.get("description")]
    return articles


def get_newsapi_news_data(ticker, from_date, to_date, max_articles=5):
    articles = fetch_newsapi_articles(ticker, from_date, to_date, max_articles)
    if len(articles) == 0:
       return 0, []
    
    text_arr = [a["description"] for a in articles]
    sentiment_scores = predict_sentiment(text_arr, ticker)
    
    sentiment_score_sum = 0
    processed_articles = [None] * len(articles)
    
    for i in range(len(articles)):
        a = articles[i]
        sentiment_score_sum += sentiment_scores[i]
        processed_articles[i] = {
            "url": a["url"],
            "title": a["title"],
            "description": a["description"],
            "author": a["author"],
            "image_url": a["urlToImage"],
            "published_utc": a["publishedAt"],
            "publisher": a["source"]["name"],
            "sentiment_score": sentiment_scores[i]
        }
    avg_sentiment = sentiment_score_sum / len(articles)

    return [avg_sentiment, processed_articles]
def get_polygon_news_data(ticker, from_date, to_date, max_articles=15):
    articles = fetch_polygon_articles(ticker, from_date, to_date, max_articles)
    if len(articles) == 0:
       return 0, []
    
    text_arr = [a.description for a in articles]
    sentiment_scores = predict_sentiment(text_arr, ticker)
    
    sentiment_score_sum = 0
    processed_articles = [None] * len(articles)
    
    for i in range(len(articles)):
        a = articles[i]
        sentiment_score_sum += sentiment_scores[i]
        processed_articles[i] = {
            "url": a.article_url,
            "title": a.title,
            "description": a.description,
            "author": a.author,
            "image_url": a.image_url,
            "published_utc": a.published_utc,
            "publisher": a.publisher.name,
            "sentiment_score": sentiment_scores[i]
        }
    avg_sentiment = sentiment_score_sum / len(articles)
    
    return [avg_sentiment, processed_articles]

def get_news_data(ticker, polygon_dates, newsapi_dates):
    polygon_sentiment, polygon_articles = get_polygon_news_data(ticker, polygon_dates[0], polygon_dates[1])
    newsapi_sentiment, newsapi_articles = get_newsapi_news_data(ticker, newsapi_dates[0], newsapi_dates[1])
    
    # Combine articles
    all_articles = polygon_articles + newsapi_articles
    all_articles.sort(
        key=lambda x: datetime.fromisoformat(x['published_utc'].replace('Z', '+00:00')),
        reverse=True
    )
    print(len(all_articles))
    # Calculate weighted average sentiment
    total_articles = len(all_articles)
    if total_articles == 0:
        return 0, []
        
    weighted_sentiment = (polygon_sentiment * len(polygon_articles) + 
                         newsapi_sentiment * len(newsapi_articles)) / total_articles
    
    return weighted_sentiment, all_articles

def get_news_data_today(ticker):
    print(f"\nGetting news data for {ticker} today")
    eastern = pytz.timezone("US/Eastern")
    now_et = datetime.now(eastern)
    print(f"Current ET time: {now_et}")

    # If it's before 4:00 a.m. ET now, use yesterday's premarket
    if now_et.time() < time(4, 0):
        polygon_start_dt = now_et.date() - timedelta(days=1)
        print("Using yesterday's premarket")
    else:
        polygon_start_dt = now_et.date()
        print("Using today's premarket")
    newsapi_start_dt = polygon_start_dt - timedelta(days=1) 
    
    polygon_start_dt  = datetime.combine(polygon_start_dt, time(4, 0))
    polygon_start_dt  = eastern.localize(polygon_start_dt).astimezone(timezone.utc)
    polygon_start_dt = polygon_start_dt .strftime("%Y-%m-%dT%H:%M:%SZ")

    newsapi_start_dt = datetime.combine(newsapi_start_dt, time(4, 0))
    newsapi_start_dt = eastern.localize(newsapi_start_dt).astimezone(timezone.utc)
    newsapi_start_dt = newsapi_start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")


    polygon_end_dt = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    newsapi_end_dt = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    polygon_dates = [polygon_start_dt, polygon_end_dt]
    newsapi_dates = [newsapi_start_dt, newsapi_end_dt]
    return get_news_data(ticker, polygon_dates, newsapi_dates)

