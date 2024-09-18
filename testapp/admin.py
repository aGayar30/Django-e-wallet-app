from django.contrib import admin
from .models import Customer, Wallet, Transaction

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'phoneNumber', 'slug')

    def user_name(self, obj):
        return obj.user.first_name
    user_name.short_description = 'Name'  # Label for the column in the admin panel



@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('customer', 'type', 'limit', 'amount', 'slug', 'isActive', 'createdAt', 'deactivatedAt')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'type', 'amount', 'beneficiary', 'date')

