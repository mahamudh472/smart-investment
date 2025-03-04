from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=[('male', 'Male'), ('female', 'Female')], blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    picture = models.ImageField(upload_to='profile/', null=True, blank=True)

    # settings
    pay_extra = models.CharField(max_length=20, default='roundup_balance', choices=(
        ('roundup_balance', 'Roundup Balance'),
        ('fixed_percentage', 'Fixed Percentage')
    ))
    pay_extra_for = models.CharField(max_length=20, default='savings', choices=(
        ('savings', 'Savings'),
        ('invest', 'Invest')
    ))
    percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return self.name()
