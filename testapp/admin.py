from django.contrib import admin
from .models import Customer, Wallet, transactions

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phoneNumber', 'slug')
    prepopulated_fields = {'slug' : ('phoneNumber',)}

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('customer', 'type', 'limit', 'amount', 'slug', 'isActive', 'createdAt', 'deactivatedAt')
@admin.register(transactions)
class transactionsAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'type', 'amount', 'benificiary', 'date', 'slug')
