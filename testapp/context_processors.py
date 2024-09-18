# testapp/context_processors.py

from .models import Wallet

AVAILABLE_WALLET_TYPES = ['current', 'savings', 'foreign']

def wallet_context(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        user_wallets = Wallet.objects.filter(customer=customer).values_list('type', flat=True)
        wallet_types = list(user_wallets)
        missing_wallet_types = [wallet_type for wallet_type in AVAILABLE_WALLET_TYPES if wallet_type not in wallet_types]
        
        return {
            'wallet_types': wallet_types,
            'missing_wallet_types': missing_wallet_types
        }
    return {
        'wallet_types': [],
        'missing_wallet_types': AVAILABLE_WALLET_TYPES
    }
