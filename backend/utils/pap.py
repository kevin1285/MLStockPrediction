import os

import pandas as pd
import numpy as np 

from keras_preprocessing.image import load_img, img_to_array

import yfinance as yf

from utils.exceptions import AppException

PAP_MODEL_PATH = 'ml_models/MulticlassPAP_20k_v2.keras'

_pap_model = None
def get_pap_model():
    global _pap_model
    if _pap_model is None:
        print("------- IMPORTING TF ---------")
        from tensorflow import keras
        print("------- LOADING PAP MODEL ---------")
        _pap_model = keras.models.load_model(PAP_MODEL_PATH, compile=False)
        print("------- PAP MODEL LOAD DONE -------")
    return _pap_model

def calculate_atr(data: pd.DataFrame, period: int) -> pd.Series:
    required_cols = ['High', 'Low', 'Close']
    if not all(col in data.columns for col in required_cols):
        raise AppException(f"ATR: Missing columns {required_cols}.", 500)

    high_low = data['High'] - data['Low']
    high_close_prev = (data['High'] - data['Close'].shift(1)).abs()
    low_close_prev = (data['Low'] - data['Close'].shift(1)).abs()

    true_range = pd.DataFrame({
        'hl': high_low,
        'hc': high_close_prev,
        'lc': low_close_prev
    }).max(axis=1, skipna=False)

    atr = true_range.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()

    if not isinstance(atr, pd.Series):
        raise AppException("ATR calculation failed.", 500)

    return atr.rename(f"ATR_{period}")


def calculate_max_drawdown(equity_series: pd.Series) -> float: #calculates max drop (captures risk)
    if equity_series is None or equity_series.empty:
        return np.nan
    cumulative_max = equity_series.cummax()
    drawdown = cumulative_max - equity_series
    max_drawdown = drawdown.max()
    return max_drawdown


def get_processed_data(ticker: str, interval: str, start_dt: str, end_dt: str, atr_period: int = 14) -> pd.DataFrame | None:
    def convert_to_et(dt_str: str) -> str:
        dt = pd.to_datetime(dt_str)
        if dt.tz is None:
            dt = dt.tz_localize('UTC')
        et = dt.tz_convert('America/New_York')
        return et.strftime('%Y-%m-%d %H:%M:%S ET')

    print(f"\n--- Processing {ticker} for Interval: {interval} from {convert_to_et(start_dt)} to {convert_to_et(end_dt)} using yfinance ---")

    valid_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d']
    if interval not in valid_intervals:
        print(f"Error: Interval '{interval}' not supported by yfinance.")
        return None

    # Fetch OHLCV data
    df = yf.download(ticker, start=start_dt, end=end_dt, interval=interval, progress=False)

    if df.empty:
        print("No data returned by yfinance.")
        return None

    if isinstance(df.columns, pd.MultiIndex):
        # keep only the first level: 'Open', 'High', ...
        df.columns = df.columns.get_level_values(0)

    df.index = pd.to_datetime(df.index, utc=True)
    df.sort_index(inplace=True)

    # Keep only necessary columns
    cols_to_keep = ['Open', 'High', 'Low', 'Close', 'Volume']
    df = df[cols_to_keep].copy()

    # Convert columns to numeric
    for col in cols_to_keep:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    rows_before_na = len(df)
    df.dropna(subset=cols_to_keep, inplace=True)
    if len(df) < rows_before_na:
        print(f"Dropped {rows_before_na - len(df)} initial NaN rows.")
    if df.empty:
        print("Data empty after initial NaN drop.")
        return None

    # Calculate ATR
    atr_col_name = f"ATR_{atr_period}"
    df[atr_col_name] = calculate_atr(df.copy(), atr_period)
    df.dropna(subset=[atr_col_name], inplace=True)

    expected_cols = cols_to_keep + [atr_col_name]
    if not all(col in df.columns for col in expected_cols):
        raise AppException(f"Final columns missing: {df.columns.tolist()}", 500)

    return df


import tempfile
import shutil
from utils.image_generation import generate_image

PAP_CONFIDENCE_THRESHOLD = 0.5
def precompute_pap_score(
    df: pd.DataFrame,
    interval_minutes: int,
    model_input_window: int,
) -> pd.DataFrame:

    # Generate image
    with tempfile.TemporaryDirectory() as temp_dir:
        image_path = generate_image(df, model_input_window, temp_dir)

        # If no images were generated, skip prediction
        if not image_path or not os.path.exists(image_path):
            return 0, "N/A"  # No valid image

        try:
            img = load_img(image_path, target_size=(128, 128), color_mode='rgb')
            img_arr = img_to_array(img)
            img_arr = np.expand_dims(img_arr, axis=0)

            pap_model = get_pap_model()
            preds = pap_model.predict(img_arr, verbose=0)
            print(preds)
            pred_index = int(np.argmax(preds))
            confidence = float(np.max(preds))

        except Exception as e:
            raise AppException(f"Error during Keras prediction: {e}", 500)

        # Assign scores based on confidence threshold
        BULLISH_INDICES_SET = {1, 2, 5}
        BEARISH_INDICES_SET = {0, 3, 4}
        
        pap_strings = ['Bearish Flag', 'Bullish Flag', 'Double Bottom', 'Double Top', 'Head & Shoulders', 'Inverted Head & Shoulders', 'Noise']
        signal_prediction, pap_prediction = 0, 'Noise'
        if pred_index != -1 and confidence >= PAP_CONFIDENCE_THRESHOLD:
            if pred_index in BULLISH_INDICES_SET:
                signal_prediction, pap_prediction = 1, pap_strings[pred_index]
            elif pred_index in BEARISH_INDICES_SET:
                signal_prediction, pap_prediction = -1, pap_strings[pred_index]
            # sanity check image
            sanity_path = os.path.join('Generated_Images', f"{pap_prediction}_{interval_minutes}_{model_input_window}.png")
            shutil.copy(image_path, sanity_path)
    return signal_prediction, pap_prediction


ATR_PERIOD = 14

from .sentiment import get_news_data_today
from datetime import datetime, timezone, timedelta


def ticker_exists(ticker: str) -> bool:
    try:
        yf.Ticker(ticker).info 
        return True
    except Exception:
        return False

def get_pap_signal(
    ticker: str,
    interval_minutes: int = 1,
    lookback_bars: int = 30,
):
    # this time delta will be set to 0 in deployment- rn it is constantly changed so we can run predictions when the market is closed
    now_dt = datetime.now(timezone.utc) - timedelta(hours=11) 

    extra = ATR_PERIOD + 10   
    df = get_processed_data(
        ticker,
        interval=f"{interval_minutes}m",
        start_dt=now_dt - pd.Timedelta(minutes=interval_minutes*(lookback_bars+extra)),
        end_dt=now_dt,
        atr_period=ATR_PERIOD
    )
    df = df.iloc[-(lookback_bars):]   # drop older rows

    # Compute PAP_Score for that window
    pap_signal, pap_pattern = precompute_pap_score(df, interval_minutes, lookback_bars)

    if pap_signal == 0:
        return 0, "N/A", df
    return pap_signal, pap_pattern, df

interval_settings = [(1, 10), (1, 15), (1, 30), (1, 45), (2, 10), (2, 15), (2, 30), (2, 45), (5, 10), (5, 15)]
def get_trade_signal(
    ticker: str,
    atr_sl_multiplier: float = 1.5,  
    rr_ratio: float = 1.5, 
):
    if not ticker_exists(ticker):
        raise AppException("Invalid ticker symbol. Please try again", 404)


    for interval_minutes, lookback_bars in interval_settings:
        print(f"-------{interval_minutes}m, {lookback_bars} bars-----")
        pap_signal, pap_pattern, df = get_pap_signal(
            ticker,
            interval_minutes=interval_minutes,
            lookback_bars=lookback_bars
        )
        if pap_signal != 0:
            break

    sent_score, articles = get_news_data_today(ticker)

    # Determine signal
    signal = None
    if pap_signal == 1:
        signal = "long"
    elif pap_signal == -1:
        signal = "short"
    else:
        if sent_score == 0:
            return "no action", "N/A", "N/A", sent_score, articles, pap_pattern
        signal = "long" if sent_score > 0 else "short"
    
    atr = df["ATR_14"].iloc[-1]
    price = df["Close"].iloc[-1]

    lows  = df["Low"].values
    highs = df["High"].values

    if signal == "long":
        support = np.min(lows)
        sl = support - atr_sl_multiplier * atr
        risk = price - sl
        tp = price + rr_ratio * risk
    else:
        resistance = np.max(highs)
        sl = resistance + atr_sl_multiplier * atr
        risk = sl - price
        tp = price - rr_ratio * risk
    return signal, sl, tp, sent_score, articles, pap_pattern