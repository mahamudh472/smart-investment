import yfinance as yf


# Fetch stock data for all symbols
def fetch_stock_list():
    symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'FB', 'TSLA', 'NVDA',
        'JPM', 'JNJ', 'V', 'PG', 'UNH', 'HD', 'MA', 'DIS',
        'PYPL', 'NFLX', 'KO', 'PFE', 'PEP'
    ]
    stock_data = []

    for symbol in symbols:
        stock = yf.Ticker(symbol)
        stock_info = stock.history(period="1d")

        # Check if we have any data available
        if not stock_info.empty:
            current_price = stock_info['Close'][0]
            stock_data.append({
                'symbol': symbol,
                'price': current_price
            })
        else:
            # Handle the case where no data is returned
            print(f"No data available for symbol: {symbol}")
            stock_data.append({
                'symbol': symbol,
                'price': None  # Or any default value you prefer
            })

    return stock_data

# # Fetch data for 20 stocks
# stock_data = fetch_stock_list(symbols)
#
# # Display the result
# for stock in stock_data:
#     print(f"Stock: {stock['symbol']}, Price: {stock['price']}")
