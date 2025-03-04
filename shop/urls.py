from django.urls import path
from . import views

app_name = "shop"
urlpatterns = [
    path('', views.shop, name="shop"),
    path('product/<int:prod_id>', views.product, name='product'),
    path('cart/', views.cart, name="cart"),
    path('add_to_cart/', views.add_to_cart, name="add_to_cart"),
    path('add_to_cart/<int:prod_id>', views.add_to_cart, name="add_to_cart_shop"),
    path('remove_cart_item/<int:item_id>', views.delete_cart_item, name="remove_cart_item"),
    path('checkout/', views.checkout, name="checkout"),
    path('payment/success', views.success, name="success"),
    path('payment/failed', views.failed, name="failed"),
    path('item_plus/<int:prod_id>', views.item_plus, name="item_plus"),
    path('item_minus/<int:prod_id>', views.item_minus, name="item_minus"),
    path('order_list/', views.orders, name="order_list")
]
