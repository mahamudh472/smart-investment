from django.urls import path, include
from main.views import index
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('accounts/', include('accounts.urls')),
    path('main/', include('main.urls')),
    path('shop/', include('shop.urls')),
    path('wallet/', include('wallet.urls')),
    path('stock/', include('stock.urls'))
]
