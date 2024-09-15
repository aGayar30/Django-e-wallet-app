from django.urls import path

from . import views

#URLCONF
urlpatterns = [
    path('', views.landing, name='landing'),  # Default route to landing page
    path('signup/', views.signup, name='signup'),  # Route for signup page
    path("home/", views.home, name='home'),
    path('add_wallet_inline/<str:wallet_type>/', views.add_wallet_inline, name='add_wallet_inline'),
    # Wallet operations
    path('wallets/deposit/<int:wallet_id>/', views.deposit, name='deposit'),
    path('wallets/withdraw/<int:wallet_id>/', views.withdraw, name='withdraw'),
    path('wallets/transfer/<int:sender_wallet_id>/', views.transfer, name='transfer'),
    path('transaction_history/<int:wallet_id>/', views.transaction_history, name='transaction_history'),

]

