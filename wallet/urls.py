from django.urls import path
from . import views

app_name = 'wallet'
urlpatterns = [
    path('', views.wallet_balance, name="wallet_balance"),
    path('transfer_balance/', views.transfer_balance, name="transfer_balance"),
    path('transactions/', views.transaction_history, name="transactions"),
    path('savings_goal/', views.goal, name='savings_goal'),
    path('delete_goal/<int:goal_id>', views.delete_goal, name='delete_goal'),
    path('goal_priority/<int:goal_priority>/<int:down>)', views.goal_priority, name='goal_priority'),
    path('lock_goal/<int:goal_id>', views.lock_goal, name="lock_goal"),
    path('unlock_goal/<int:goal_id>', views.unlock_goal, name="unlock_goal"),

]
