from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from wallet.models import Transaction
from .utils import fetch_stock_list
from .models import Stock, Investment, InvestmentTransaction
import yfinance as yf


@login_required(login_url='accounts:login')
def stock_list(request):
    stocks = Stock.objects.all()

    context = {
        'stock_list': stocks
    }
    return render(request, 'stock/stock_list.html', context)


@login_required(login_url='accounts:login')
def get_stock_history(symbol, period="1mo"):
    stock = yf.Ticker(symbol)
    stock_history = stock.history(period=period)

    return stock_history


@login_required(login_url='accounts:login')
def stock_chart(request, symbol):
    # Fetch historical data for the stock

    period = request.GET.get('period', '1y')
    stock = yf.Ticker(symbol)
    stock_history = stock.history(period=period)  # Last 1 month of data
    sym = Stock.objects.get(symbol=symbol)
    temp = Investment.objects.filter(stock_symbol=sym)
    holdings = 0
    if temp.exists():
        holdings = temp.first().shares
    # Prepare data for the chart
    dates = stock_history.index.strftime('%Y-%m-%d').tolist()
    prices = stock_history['Close'].tolist()
    current_price = f"{prices[-1]:.2f}"
    transactions = []
    if temp.exists():
        transactions = temp.first().transactions.all()
    context = {
        'symbol': symbol,
        'dates': dates,
        'prices': prices,
        'period': period,
        'current_price': current_price,
        'holdings': holdings,
        'transactions': transactions
    }

    return render(request, 'stock/stock chart.html', context)


@login_required(login_url='accounts:login')
def user_stocks(request):
    return render(request, 'stock/user_stocks.html')


@login_required(login_url='accounts:login')
def buy_stock(request):
    if request.method == "POST":
        amount = Decimal(request.POST.get('amount'))
        symbol = request.POST.get('symbol')
        wallet = request.user.wallet
        if amount > wallet.investment_balance:
            return redirect('stock:user_stocks')
        stock = Stock.objects.get(symbol=symbol)
        shares = Decimal(amount) / stock.current_price
        temp = Investment.objects.filter(stock_symbol=symbol, user=request.user)

        if temp.exists():
            temp.first().buy_more_shares(amount, stock.current_price)
        else:
            Investment.objects.get_or_create(
                user=request.user,
                stock_symbol=symbol,
                purchase_price=stock.current_price,
                shares=shares,
                invested_amount=Decimal(amount)
            )
        inv = Investment.objects.filter(user=request.user, stock_symbol=symbol).last()
        print(inv)
        InvestmentTransaction.objects.create(
            investment=inv,
            shares=shares,
            purchase_price=stock.current_price,
            invested_amount=amount
        )
        wallet.investment_balance -= amount
        wallet.add_transaction(
            amount=amount,
            transaction_type='Invest',
            account="Current"
        )
        wallet.save()
    return redirect('stock:user_stocks')


@login_required(login_url='accounts:login')
def sell_stock(request):
    if request.method == "POST":
        shares = Decimal(request.POST.get('shares'))
        symbol = request.POST.get('symbol')

        stock = Stock.objects.get(symbol=symbol)
        temp = Investment.objects.filter(user=request.user, stock_symbol=symbol)
        amount = shares * stock.current_price
        if temp.exists():
            if temp.first().shares >= shares:
                temp.first().sell_shares(shares, stock.current_price)

                InvestmentTransaction.objects.create(
                    investment=temp.first(),
                    shares=shares,
                    purchase_price=stock.current_price,
                    invested_amount=amount,
                    transaction_type="Sell"
                )
                wallet = request.user.wallet
                wallet.add_transaction(
                    amount=amount,
                    transaction_type='Sell stock',
                    account="Current"
                )

    return redirect('stock:user_stocks')
