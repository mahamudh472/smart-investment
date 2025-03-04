# stock/management/commands/update_stock_data.py
from django.core.management.base import BaseCommand
import yfinance as yf
from stock.models import Stock


class Command(BaseCommand):
    help = 'Fetches and updates stock data daily'

    def handle(self, *args, **kwargs):
        symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA',
            'JPM', 'JNJ', 'V', 'PG', 'UNH', 'HD', 'MA', 'DIS',
            'PYPL', 'NFLX', 'KO', 'PFE', 'PEP'
        ]

        for symbol in symbols:
            stock = yf.Ticker(symbol)
            stock_info = stock.history(period="1d")

            if not stock_info.empty:
                current_price = stock_info['Close'][0]
                daily_high = stock_info['High'][0]
                daily_low = stock_info['Low'][0]
                previous_close = stock_info['Close'][1] if len(stock_info['Close']) > 1 else current_price

                # Update or create stock in the database
                Stock.objects.update_or_create(
                    symbol=symbol,
                    defaults={
                        'current_price': current_price,
                        'daily_high': daily_high,
                        'daily_low': daily_low,
                        'previous_close': previous_close,
                    }
                )

        self.stdout.write(self.style.SUCCESS("Stock data updated successfully"))
