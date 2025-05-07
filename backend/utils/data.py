def fetch_data(client, symbol, multiplier, timespan, start, end):
    aggs = client.list_aggs(
        ticker=symbol,
        multiplier=multiplier,
        timespan=timespan,
        from_=start,
        to=end,
        limit=50000 # Max limit per request
    )
    df = pd.DataFrame(aggs)

    # prepreocessing
    if not df.empty:
        df['t'] = pd.to_datetime(df['t'], unit='ms')
        df = df.set_index('t')
        df = df.rename(columns={
            'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume'
        })
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']] # Keep relevant columns
        # Ensure data is sorted chronologically
        df = df.sort_index()
    return df