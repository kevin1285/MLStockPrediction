import os

from polygon import RESTClient

import pandas as pd
import numpy as np 

from keras_preprocessing.image import load_img, img_to_array

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
client = RESTClient(POLYGON_API_KEY)

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
        raise ValueError(f"ATR: Missing columns {required_cols}.")

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
        raise TypeError("ATR calculation failed.")

    return atr.rename(f"ATR_{period}")


def calculate_max_drawdown(equity_series: pd.Series) -> float: #calculates max drop (captures risk)
    if equity_series is None or equity_series.empty:
        return np.nan
    cumulative_max = equity_series.cummax()
    drawdown = cumulative_max - equity_series
    max_drawdown = drawdown.max()
    return max_drawdown


def get_processed_data(ticker: str, interval: str, start_dt: str, end_dt: str, atr_period: int = 14) -> pd.DataFrame | None:
    def convert_to_et(dt_str: str) -> str: # only used for print()
        dt = pd.to_datetime(dt_str)
        if dt.tz is None:
            dt = dt.tz_localize('UTC')
        et = dt.tz_convert('America/New_York')
        return et.strftime('%Y-%m-%d %H:%M:%S ET')

    print(f"\n--- Processing {ticker} for Interval: {interval} from {convert_to_et(start_dt)} to {convert_to_et(end_dt)} using Polygon.io ---")
    interval_map_poly = {'1m': (1, 'minute'), '5m': (5, 'minute'), '15m': (15, 'minute'), '30m': (30, 'minute'), '60m': (1, 'hour')}
    interval_map_pd = {'1m': '1min', '5m': '5min', '15m': '15min', '30m': '30min', '60m': 'H'}

    if interval not in interval_map_poly:
       print(f"Error: Interval '{interval}' not mapped for Polygon.io.")
       return None

    multiplier, timespan = interval_map_poly[interval]
    pd_freq = interval_map_pd[interval]
    print(f"Requesting Polygon.io: Symbol={ticker}, Multiplier={multiplier}, Timespan={timespan}, Start={convert_to_et(start_dt)}, End={convert_to_et(end_dt)}")
    all_aggs_data = []

    aggs_iterator = client.list_aggs(ticker=ticker, multiplier=multiplier, timespan=timespan, from_=start_dt, to=end_dt, adjusted=True, limit=50000)
    for agg in aggs_iterator:
        all_aggs_data.append({'timestamp': agg.timestamp, 'open': agg.open, 'high': agg.high, 'low': agg.low, 'close': agg.close, 'volume': agg.volume})

    raw_df = pd.DataFrame(all_aggs_data)

    print(raw_df.columns.tolist())
    # Processing
    raw_df['timestamp'] = pd.to_datetime(raw_df['timestamp'], unit='ms', utc=True)
    raw_df.set_index('timestamp', inplace=True)

    rename_map = {'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}
    raw_df.rename(columns=rename_map, inplace=True)
    cols_to_keep = ['Open', 'High', 'Low', 'Close', 'Volume']

    processed_data = raw_df[[col for col in cols_to_keep if col in raw_df.columns]].copy()
    processed_data.sort_index(ascending=True, inplace=True)

    for col in cols_to_keep:
        if col in processed_data.columns:
            processed_data[col] = pd.to_numeric(processed_data[col], errors='coerce')

    rows_before_na = len(processed_data); processed_data.dropna(subset=cols_to_keep, inplace=True)
    if len(processed_data) < rows_before_na:
        print(f"Dropped {rows_before_na - len(processed_data)} initial NaN rows.")
    if processed_data.empty:
        print("Data empty after initial NaN drop."); return None

    # Calculate ATR
    atr_col_name = f"ATR_{atr_period}"
    processed_data[atr_col_name] = calculate_atr(processed_data.copy(), atr_period)
    rows_before_atr_na=len(processed_data)
    processed_data.dropna(subset=[atr_col_name], inplace=True)
    rows_after_atr_na=len(processed_data)

    final_expected_cols=cols_to_keep+[atr_col_name];
    if not all(col in processed_data.columns for col in final_expected_cols):
        raise ValueError(f"Final columns missing: {processed_data.columns.tolist()}")
    return processed_data


import tempfile
from utils.image_generation import generate_image

PAP_CONFIDENCE_THRESHOLD = 0.5
def precompute_pap_scores_sequential_img_batched_pred(
    df: pd.DataFrame,
    model_input_window: int,
    batch_size: int = 64
) -> pd.DataFrame:

    # Initialize score column
    df['PAP_Score'] = 0
    pap_scores = df['PAP_Score'].values

    image_paths_dict = {}
    lookback = model_input_window - 1

    # Generate image
    with tempfile.TemporaryDirectory() as temp_dir:
        tasks_args = [
            (i, df, model_input_window, temp_dir)
            for i in range(lookback, len(df))
        ]
        for args in tasks_args:
            original_index, image_path = generate_image(args)
            if image_path and os.path.exists(image_path):
                image_paths_dict[original_index] = image_path

        # If no images were generated, skip prediction
        if not image_paths_dict:
            print("Warning: No images generated. Skipping prediction.")
            df['PAP_Score'] = pap_scores
            return df

        # Keras prediction
        indices_to_predict = sorted(image_paths_dict.keys())
        ordered_image_paths = [image_paths_dict[i] for i in indices_to_predict]
        num_images = len(ordered_image_paths)

        all_pred_indices = np.full(num_images, -1, dtype=int)
        all_pred_confidences = np.full(num_images, -1.0, dtype=float)
        try:
            print(f"Preparing {num_images} images for Keras batch prediction...")
            img_array_list = []
            load_failures = 0
            for i, img_path in enumerate(ordered_image_paths):
                try:
                    img = load_img(img_path, target_size=(128, 128), color_mode='rgb')
                    img_arr = img_to_array(img)
                    img_array_list.append(img_arr)
                except Exception as load_err:
                    print(f"Warning: Keras load failed index {indices_to_predict[i]} ({img_path}): {load_err}")
                    img_array_list.append(np.zeros((128, 128, 3), dtype=np.uint8))
                    load_failures += 1

            if img_array_list:
                keras_batch = np.stack(img_array_list, axis=0)
                pap_model = get_pap_model()
                raw_preds_batch = pap_model.predict(keras_batch, batch_size=batch_size, verbose=1)
                
                print("--------PROBS--------")
                print(raw_preds_batch)

                if raw_preds_batch.shape[0] == num_images:
                    all_pred_indices = np.argmax(raw_preds_batch, axis=1).astype(int)
                    print(all_pred_indices)
                    all_pred_confidences = np.max(raw_preds_batch, axis=1).astype(float)
                else:
                    print("Prediction output shape mismatch.")
            else:
                print("No images successfully loaded for Keras prediction.")

            if load_failures > 0:
                print(f"Warning: {load_failures} images failed to load.")

        except Exception as e:
            print(f"ERROR during Keras batch prediction: {e}")

        # Assign scores based on confidence threshold
        print("Stage 3: Assigning scores (1/-1/0) based on confidence threshold...")
        BULLISH_INDICES_SET = {1, 2, 5}
        BEARISH_INDICES_SET = {0, 3, 4}
        
        paps = ['BearishFlag', 'BullishFlag', 'DoubleBottom', 'DoubleTop', 'HS', 'IHS', 'Noise']
        prediction_to_string = None
        for i, original_index in enumerate(indices_to_predict):
            predicted_index = all_pred_indices[i]
            confidence = all_pred_confidences[i]
            if predicted_index != -1 and confidence >= PAP_CONFIDENCE_THRESHOLD:
                if predicted_index in BULLISH_INDICES_SET:
                    pap_scores[original_index] = 1
                elif predicted_index in BEARISH_INDICES_SET:
                    pap_scores[original_index] = -1
                prediction_to_string = paps[predicted_index]
                print(prediction_to_string)

    df['PAP_Score'] = pap_scores
    return df, prediction_to_string

ATR_PERIOD = 14
MODEL_INPUT_WINDOW = 30 # Number of bars for the input image
PAP_LOOKBACK = MODEL_INPUT_WINDOW - 1
SENTIMENT_THRESHOLD = 0.

INTERVAL_MULTIPLIER = 1
INTERVAL_TIMESPAN = 'minute'

PREDICTION_BATCH_SIZE = 64 # Batch size for CNN prediction

from .sentiment import get_news_data_today
from datetime import datetime, timezone, timedelta


def ticker_exists(ticker: str) -> bool:
    try:
        client.get_ticker_details(ticker)
        return True
    except Exception:
        return False
    
def get_trade_signal(
    ticker: str,
    lookback_bars: int = MODEL_INPUT_WINDOW,
    atr_period: int = ATR_PERIOD,
    atr_sl_multiplier: float = 1.5,  
    rr_ratio: float = 1.5, 
) -> str:
    if not ticker_exists(ticker):
        raise ValueError("Ticker does not exist")
    # this time delta will be set to 0 in deployment- rn it is constantly changed so we can run predictions when the market is closed
    now_dt = datetime.now(timezone.utc) - timedelta(hours=19) 

    extra = atr_period + 10   
    df = get_processed_data(
        ticker,
        interval=f"{INTERVAL_MULTIPLIER}{INTERVAL_TIMESPAN[0]}",
        start_dt=now_dt - pd.Timedelta(minutes=INTERVAL_MULTIPLIER*(lookback_bars+extra)),
        end_dt=now_dt,
        atr_period=atr_period
    )
    df = df.iloc[-(lookback_bars):]   # drop older rows

    # Compute PAP_Score for that window
    df, pap_pattern = precompute_pap_scores_sequential_img_batched_pred(
        df=df,
        model_input_window=lookback_bars,
        batch_size=PREDICTION_BATCH_SIZE
    )

    # Compute today's sentiment (this returns a float)
    sent_score, articles = get_news_data_today(ticker)

    # Compute ATR, PAP, Price
    atr = df["ATR_14"].iloc[-1]
    pap = int(df["PAP_Score"].iloc[-1])
    price = df["Close"].iloc[-1]

    # Sanity checks
    if any(np.isnan(x) or x <= 0 for x in (atr, price)):
        print("SANITY CHECK FAILED")
        return "hold", sent_score, articles, pap_pattern

    # Determine signal
    signal = None
    if pap == 1:
        signal = "long"
    elif pap == -1:
        signal = "short"
    else:
        if sent_score == 0:
            return "no action", price, price, sent_score, articles, pap_pattern
        signal = "long" if sent_score > 0 else "short"
    
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