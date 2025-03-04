# models.py
from django.contrib.auth.models import User
from django.db import models


class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    daily_high = models.DecimalField(max_digits=10, decimal_places=2)
    daily_low = models.DecimalField(max_digits=10, decimal_places=2)
    previous_close = models.DecimalField(max_digits=10, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.symbol


class Investment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock_symbol = models.CharField(max_length=50, blank=True, null=True)
    shares = models.DecimalField(max_digits=10, decimal_places=5)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    invested_amount = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)

    @property
    def get_shares_value(self):
        stock_symbol = Stock.objects.get(symbol=self.stock_symbol)
        return f"{self.shares * stock_symbol.current_price:.2f}"

    def buy_more_shares(self, additional_amount, additional_price):
        additional_shares = additional_amount / additional_price
        self.invested_amount += additional_amount
        self.shares += additional_shares
        # Calculate the new weighted average purchase price
        self.purchase_price = self.invested_amount / self.shares
        self.save()
        return

    def sell_shares(self, shares, current_price):
        amount = shares * current_price
        self.invested_amount -= amount
        self.shares -= shares
        self.save()
        self.user.wallet.investment_balance += amount
        self.user.wallet.save()
        profit = (shares * current_price) - (shares * self.purchase_price)
        stock_obj = Stock.objects.get(symbol=self.stock_symbol)
        Profit.objects.create(
            stock=stock_obj,
            user=self.user,
            amount=profit
        )
        return


class InvestmentTransaction(models.Model):
    investment = models.ForeignKey(Investment, related_name='transactions', on_delete=models.CASCADE)
    shares = models.DecimalField(max_digits=10, decimal_places=5)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)  # Individual purchase price
    invested_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount invested in this transaction
    transaction_type = models.CharField(max_length=20, default="Buy")
    purchase_date = models.DateTimeField(auto_now_add=True)


class Profit(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
