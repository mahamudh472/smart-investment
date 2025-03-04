from django.db import models
from django.contrib.auth.models import User
import uuid


# Create your models here.

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    savings_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    investment_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wallet_status = models.BooleanField(default=True)  # active or inactive

    def __str__(self):
        return f"Wallet of {self.user}"

    def add_transaction(self, amount, transaction_type, description=None, account=None):
        Transaction.objects.create(
            wallet=self,
            amount=amount,
            transaction_type=transaction_type,
            description=description,
            account=account
        )

    def get_monthly_profit(self):
        total = 0
        for item in self.user.profit_set.all():
            total += item.amount
        return total

    def add_goal(self, name, amount):
        priority = 1 if not self.savings_goals.exists() else self.savings_goals.last().priority + 1
        SavingsGoal.objects.create(
            wallet=self,
            name=name,
            target_amount=amount,
            priority=priority
        )
        return

    def generate_goal_percentage(self):
        total_balance = self.savings_balance
        locked_items = self.savings_goals.filter(is_locked=True)
        for item in locked_items:
            if total_balance >= item.target_amount:
                item.percentage = 100
                total_balance -= item.target_amount
                item.save()
            else:
                item.percentage = (total_balance / item.target_amount) * 100
                item.save()
                total_balance = 0

        unlocked_items = self.savings_goals.filter(is_locked=False)
        for item in unlocked_items:
            if total_balance >= item.target_amount:
                item.percentage = 100
                total_balance -= item.target_amount
                item.save()
            else:
                item.percentage = (total_balance / item.target_amount) * 100
                item.save()
                total_balance = 0

    def change_goal_priority(self, goal_priority, down=False):
        if down:
            next_item = self.savings_goals.get(priority=goal_priority + 1)
            curr_item = self.savings_goals.get(priority=goal_priority)
            curr_item.priority += 1
            next_item.priority -= 1

        else:
            next_item = self.savings_goals.get(priority=goal_priority - 1)
            curr_item = self.savings_goals.get(priority=goal_priority)
            curr_item.priority -= 1
            next_item.priority += 1

        next_item.save()
        curr_item.save()


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
        ('payment', 'Payment')
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    account = models.CharField(max_length=50, blank=True, null=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} to wallet {self.wallet.id} on {self.created_at}"


class SavingsGoal(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='savings_goals')
    name = models.CharField(max_length=100, default='Untitled')
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    priority = models.PositiveIntegerField()
    is_locked = models.BooleanField(default=False)
    percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['priority']  # Automatically order by priority

    def progress_percentage(self):
        """Returns the progress of the goal as a percentage."""
        if self.wallet.savings_balance >= self.target_amount:
            current_amount = self.wallet.savings_balance - self.target_amount
        else:
            current_amount = self.wallet.savings_balance
        return (current_amount / self.target_amount) * 100 if self.target_amount > 0 else 0
