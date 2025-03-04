import math
from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from stock.models import Stock, Investment, InvestmentTransaction
from wallet.models import Wallet
from .models import Product, Cart, CartItem, Order, OrderItem
from django.http import JsonResponse


# Create your views here.

def shop(request):
    cart_item_ids = []
    products = Product.objects.all()
    if request.user.is_authenticated:
        user_cart = Cart.objects.filter(user=request.user)
        if user_cart.exists():
            for item in user_cart.first().items.all():
                cart_item_ids.append(item.product_id)
    context = {
        'products': products,
        'cart_item_ids': cart_item_ids
    }
    return render(request, 'shop/shop.html', context)


def product(request, prod_id):
    cart_item_ids = []
    prod = Product.objects.get(id=prod_id)
    if request.user.is_authenticated:
        user_cart = Cart.objects.filter(user=request.user)
        if user_cart.exists():
            for item in user_cart.first().items.all():
                cart_item_ids.append(item.product_id)
    context = {
        'product': prod,
        'cart_item_ids': cart_item_ids
    }
    return render(request, 'shop/product.html', context)


@login_required(login_url='accounts:login')
def cart(request):
    return render(request, 'shop/cart.html')


@login_required(login_url='accounts:login')
def add_to_cart(request, prod_id=None):
    # Unpack the tuple returned by get_or_create
    user_cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        prod_name = request.POST.get('product_name')
        quantity = request.POST.get('quantity')
        try:
            # Get the product using get_object_or_404 for better error handling
            prod = get_object_or_404(Product, name=prod_name)

            # Create the CartItem
            item, created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=prod,
                quantity=quantity
            )

            item.save()

            # Return success response with cart count
            return JsonResponse({'success': 'Item added to cart.', 'cart_count': user_cart.cart_count})

        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found.'})
        except Exception as e:
            # Catch specific errors and send appropriate messages
            return JsonResponse({'error': f"Add to cart failed: {str(e)}"})
    if prod_id:
        prod = get_object_or_404(Product, id=prod_id)
        # Create the CartItem
        item, created = CartItem.objects.get_or_create(
            cart=user_cart,
            product=prod,
        )
        item.save()
        return redirect('shop:shop')

    return JsonResponse({'error': 'Invalid request method.'})


@login_required(login_url='accounts:login')
def delete_cart_item(request, item_id):
    item = CartItem.objects.get(id=item_id, cart__user=request.user)
    item.delete()
    return redirect('shop:cart')


@login_required(login_url='accounts:login')
def item_plus(request, prod_id):
    item = CartItem.objects.get(id=prod_id, cart__user=request.user)
    item.quantity += 1
    item.save()
    return redirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='accounts:login')
def item_minus(request, prod_id):
    item = CartItem.objects.get(id=prod_id, cart__user=request.user)
    item.quantity -= 1
    item.save()
    if item.quantity == 0:
        item.delete()
    return redirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='accounts:login')
def checkout(request):
    if request.method == 'POST':
        wallet = Wallet.objects.get(user=request.user)
        user_cart = Cart.objects.get(user=request.user)
        pay_extra = request.POST.get('pay_extra')
        total_price = 0

        order = Order.objects.create(
            user=request.user,
        )
        order.save()

        for item in user_cart.items.all():
            total_price += item.total_price
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )
        if pay_extra == "roundup_balance":
            roundup_price = math.ceil(total_price)
        else:
            percentage = request.POST.get('percentage')
            roundup_price = total_price + (total_price * Decimal(percentage) / 100)
        roundup_amount = roundup_price - total_price
        payment_method = request.POST.get('payment_method')
        if payment_method == 'current' and wallet.investment_balance >= total_price:
            wallet.investment_balance -= Decimal(roundup_price)
            wallet.save()
            wallet.add_transaction(
                amount=roundup_price,
                transaction_type="payment",
                account='Current'
            )
            pay_extra_for = request.POST.get('pay_extra_for')
            if pay_extra_for == 'savings':
                wallet.savings_balance += roundup_amount
                wallet.add_transaction(
                    amount=roundup_amount,
                    transaction_type="Roundup",
                    account='Savings'
                )
                wallet.save()
            else:
                stock_id = request.POST.get('selected_stock')
                selected_stock = Stock.objects.get(id=stock_id)
                shares = roundup_amount / selected_stock.current_price
                temp = Investment.objects.filter(stock_symbol=selected_stock)
                if temp.exists():
                    temp.first().buy_more_shares(roundup_amount, selected_stock.current_price)
                else:
                    Investment.objects.get_or_create(
                        user=request.user,
                        stock_symbol=selected_stock,
                        purchase_price=selected_stock.current_price,
                        shares=shares,
                        invested_amount=Decimal(roundup_amount)
                    )
                inv = Investment.objects.filter(user=request.user, stock_symbol=selected_stock).last()

                InvestmentTransaction.objects.create(
                    investment=inv,
                    shares=shares,
                    purchase_price=selected_stock.current_price,
                    invested_amount=roundup_amount
                )
                wallet.add_transaction(
                    amount=roundup_amount,
                    transaction_type="Invest",
                    account='Roundup'
                )
            request.session['roundup_amount'] = float(roundup_amount)
            request.session['total_price'] = float(total_price)
            request.session['roundup_price'] = float(roundup_price)
            return redirect('shop:success')

        elif payment_method == 'stripe':
            pass
    stocks = Stock.objects.order_by('?')[:5]
    return render(request, 'shop/checkout.html', {'stock_list': stocks})


def success(request):
    request.user.cart.items.all().delete()
    return render(request, 'shop/success.html')


def failed(request):
    return render(request, 'shop/failed.html')


@login_required(login_url='accounts:login')
def orders(request):
    return render(request, 'shop/order_list.html')
