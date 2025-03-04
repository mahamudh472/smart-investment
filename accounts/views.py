from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .decorators import redirect_if_authenticated
from .models import UserProfile, User
from wallet.models import Wallet


@redirect_if_authenticated
def loginView(request):
    if request.method == "POST":
        username = request.POST.get('email')
        password = request.POST.get('password')

        # Try authenticating with the provided username (email or username)
        user = authenticate(request, username=username, password=password)

        # If authentication fails and email contains '@', try using the part before '@' as username
        if not user and '@' in username:
            username = username.split('@')[0]
            user = authenticate(request, username=username, password=password)

        # Handle successful or failed authentication
        if user:
            login(request, user)
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Authentication Error')
            return redirect('accounts:login')

    return render(request, 'accounts/login.html')


@redirect_if_authenticated
def registerView(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        username = email.split('@')[0]
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return redirect('accounts:register')
        if password2 != password:
            messages.error(request, 'Password and confirm password not matched!')
            return redirect('accounts:register')
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password
        )
        user.save()
        up = UserProfile.objects.create(
            user=user
        )
        up.save()
        Wallet.objects.create(user=user)
        login(request, user)
        return redirect('main:dashboard')
    return render(request, 'accounts/register.html')


def logoutView(request):
    logout(request)
    return redirect('accounts:login')


def update_settings(request):
    if request.method == "POST":
        pay_extra = request.POST.get('pay_extra')
        pay_extra_for = request.POST.get('pay_extra_for')
        p = request.user.userprofile

        p.pay_extra = pay_extra
        p.percentage = Decimal(request.POST.get('percentage'))

        p.pay_extra_for = pay_extra_for
        p.save()
        return redirect(request.META.get('HTTP_REFERER'))

