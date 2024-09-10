from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Customer, Wallet, transactions
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login




# Create your views here.


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

        # Create a wallet for the new customer
        wallet_slug = slugify(f"{new_customer.phoneNumber}-current")
        new_wallet = Wallet(customer=new_customer, type='current', amount=0, slug=wallet_slug)
        new_wallet.save()

        # Automatically log in the user after signup
        from django.contrib.auth import login
        login(request, user)  # Log the user in
        return redirect('home')  # Redirect to home page after successful signup

    return render(request, 'signup.html')



def landing(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        user = authenticate(username=phone, password=password)  # Django authentication

        if user is not None:
            login(request, user)  # Log the user in
            return redirect('home')  # Redirect to home page
        else:
            messages.error(request, 'Invalid phone number or password.')

    return render(request, 'landing.html')




# Predefined wallet types
AVAILABLE_WALLET_TYPES = ['current', 'savings', 'foreign']

def home(request):
    if request.user.is_authenticated:
        customer = request.user.customer

        # Get all wallet types that the user has created
        user_wallets = Wallet.objects.filter(customer=customer).values_list('type', flat=True)

        # List the wallet types the user has and the missing wallet types
        wallet_types = user_wallets
        missing_wallet_types = [wallet for wallet in AVAILABLE_WALLET_TYPES if wallet not in user_wallets]

        # Get the current wallet by type from the query string (or default to 'current')
        wallet_type = request.GET.get('wallet_type', 'current')

        # Fetch the current wallet to display
        try:
            current_wallet = Wallet.objects.get(customer=customer, type=wallet_type)
        except Wallet.DoesNotExist:
            current_wallet = None

        return render(request, 'Home.html', {
            'wallet': current_wallet,
            'wallet_types': wallet_types,
            'missing_wallet_types': missing_wallet_types
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


def deposit(request, wallet_id):
    if request.method == 'POST':
        amount = int(request.POST.get('amount'))
        wallet = Wallet.objects.get(id=wallet_id)

        # Increase the wallet amount
        wallet.amount += amount
        wallet.save()

        # Save the transaction
        transaction = transactions(
            wallet=wallet,
            type='deposit',
            amount=amount,
            benificiary=wallet.customer.phoneNumber,
        )
        transaction.save()

        messages.success(request, f'Deposited {amount} to your wallet.')
        return redirect('home')  # Redirect to the wallets page

    return render(request, 'deposit.html', {'wallet_id': wallet_id})


def withdraw(request, wallet_id):
    if request.method == 'POST':
        amount = int(request.POST.get('amount'))
        wallet = Wallet.objects.get(id=wallet_id)

        # Check if there is enough balance
        if wallet.amount >= amount:
            wallet.amount -= amount
            wallet.save()

            # Save the transaction
            transaction = transactions(
                wallet=wallet,
                type='withdraw',
                amount=amount,
                benificiary=wallet.customer.phoneNumber,
            )
            transaction.save()

            messages.success(request, f'Withdrew {amount} from your wallet.')
        else:
            messages.error(request, 'Insufficient funds.')

        return redirect('home')  # Redirect to the wallets page

    return render(request, 'withdraw.html', {'wallet_id': wallet_id})

def transfer(request, sender_wallet_id):
    if request.method == 'POST':
        amount = int(request.POST.get('amount'))
        receiver_phone = request.POST.get('receiver_phone')

        sender_wallet = Wallet.objects.get(id=sender_wallet_id)

        try:
            # Get receiver wallet using the phone number
            receiver_customer = Customer.objects.get(phoneNumber=receiver_phone)
            receiver_wallet = Wallet.objects.get(customer=receiver_customer, type='current')

            # Check if sender has enough balance
            if sender_wallet.amount >= amount:
                # Deduct from sender
                sender_wallet.amount -= amount
                sender_wallet.save()

                # Add to receiver
                receiver_wallet.amount += amount
                receiver_wallet.save()

                # Save the transaction for sender (transfer-out)
                transaction_sender = transactions(
                    wallet=sender_wallet,
                    type='transfer-out',
                    amount=amount,
                    benificiary=receiver_customer.phoneNumber,  # Receiver's phone number
                )
                transaction_sender.save()

                # Save the transaction for receiver (transfer-in)
                transaction_receiver = transactions(
                    wallet=receiver_wallet,
                    type='transfer-in',
                    amount=amount,
                    benificiary=sender_wallet.customer.phoneNumber,  # Sender's phone number
                )
                transaction_receiver.save()

                messages.success(request, f'Transferred {amount} to {receiver_customer.phoneNumber}.')
            else:
                messages.error(request, 'Insufficient funds.')

        except Customer.DoesNotExist:
            messages.error(request, 'Receiver does not exist.')

        return redirect('home')  # Redirect to the wallets page

    return render(request, 'transfer.html', {'sender_wallet_id': sender_wallet_id})



