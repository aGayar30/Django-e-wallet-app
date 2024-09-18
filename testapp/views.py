from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.utils.text import slugify

from .models import Customer, Transaction, Wallet


def signup(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        re_enter_password = request.POST.get('reEnterPassword')

        if password != re_enter_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')

        # Create User
        user = User.objects.create_user(username=phone, password=password, email=email)
        user.first_name = name
        user.save()

        # Create Customer linked to the User
        slug = slugify(phone)
        new_customer = Customer(user=user, phoneNumber=phone, slug=slug)
        new_customer.save()

        # Create a default wallet (current)
        Wallet.create_wallet(customer=new_customer, wallet_type='current')

        # Automatically log in the user after signup
        login(request, user)
        return redirect('home')

    return render(request, 'signup.html')


def landing(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        user = authenticate(username=phone, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid phone number or password.')

    return render(request, 'landing.html')


# Predefined wallet types
AVAILABLE_WALLET_TYPES = ['current', 'savings', 'foreign']

# testapp/views.py

def home(request):
    if request.user.is_authenticated:
        customer = request.user.customer

        # Get the current wallet by type from the query string (or default to 'current')
        wallet_type = request.GET.get('wallet_type', 'current')
        current_wallet = Wallet.objects.filter(customer=customer, type=wallet_type).first()

        return render(request, 'Home.html', {
            'wallet': current_wallet,
        })
    else:
        return redirect('landing')


def deposit(request, wallet_id):
    if request.method == 'POST':
        amount = int(request.POST.get('amount'))
        wallet = Wallet.objects.get(id=wallet_id)
        
        # Call deposit method in the Wallet model
        wallet.deposit(amount)
        
        messages.success(request, f'Deposited {amount} to your wallet.')
        return redirect('home')

    return render(request, 'deposit.html', {'wallet_id': wallet_id})


def withdraw(request, wallet_id):
    if request.method == 'POST':
        amount = int(request.POST.get('amount'))
        wallet = Wallet.objects.get(id=wallet_id)
        
        try:
            # Call withdraw method in the Wallet model
            wallet.withdraw(amount)
            messages.success(request, f'Withdrew {amount} from your wallet.')
        except ValueError as e:
            messages.error(request, str(e))

        return redirect('home')

    return render(request, 'withdraw.html', {'wallet_id': wallet_id})


def transfer(request, sender_wallet_id):
    if request.method == 'POST':
        amount = int(request.POST.get('amount'))
        receiver_phone = request.POST.get('receiver_phone')

        sender_wallet = Wallet.objects.get(id=sender_wallet_id)

        try:
            # Get receiver's wallet
            receiver_customer = Customer.objects.get(phoneNumber=receiver_phone)
            receiver_wallet = Wallet.objects.get(customer=receiver_customer, type='current')

            # Perform transfer
            sender_wallet.transfer(amount, receiver_wallet)
            messages.success(request, f'Transferred {amount} to {receiver_customer.phoneNumber}.')
        except Customer.DoesNotExist:
            messages.error(request, 'Receiver does not exist.')
        except ValueError as e:
            messages.error(request, str(e))

        return redirect('home')

    return render(request, 'transfer.html', {'sender_wallet_id': sender_wallet_id})


def transaction_history(request, wallet_id):
    if request.user.is_authenticated:
        customer = request.user.customer
        wallet = Wallet.objects.get(id=wallet_id, customer=customer)

        transactions_list = Transaction.objects.filter(wallet=wallet).order_by('-date')
        
        return render(request, 'transactionhistory.html', {
            'wallet': wallet,
            'transactions': transactions_list,
        })
    else:
        return redirect('landing')

def add_wallet_inline(request, wallet_type):
    if request.user.is_authenticated:
        customer = request.user.customer

        # Get all wallet types that the user has created
        user_wallets = Wallet.objects.filter(customer=customer).values_list('type', flat=True)

        # Check if the selected wallet type is valid and not already created
        if wallet_type in AVAILABLE_WALLET_TYPES and wallet_type not in user_wallets:
            wallet_slug = slugify(f"{customer.phoneNumber}-{wallet_type}")
            new_wallet = Wallet(customer=customer, type=wallet_type, slug=wallet_slug)
            new_wallet.save()
            messages.success(request, f'{wallet_type.capitalize()} wallet created successfully.')
        else:
            messages.error(request, 'Invalid wallet type or wallet already exists.')

        return redirect('home')
    else:
        return redirect('landing')