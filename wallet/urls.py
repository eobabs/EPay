from django.urls import path
from . import views

urlpatterns = [
    # path('welcome/', views.welcome, name='welcome'),
    # path('greet/<str:name>', views.greeting, name='greeting'),
    # path('welcome_New/', views.welcome_New, name='welcome'),
    path('fund/account', views.fund_wallet, name='fund_wallet'),
    path('fund/verify', views.verify_fund, name='verify_fund'),

    path('fund/verify_withdraw', views.verify_withdraw, name='verify_withdraw'),
    path('fund/transfer', views.transfer, name='transfer'),
    path('fund/withdraw', views.withdraw, name='withdraw')
]