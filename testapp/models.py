from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
import uuid

# Predefined wallet types
AVAILABLE_WALLET_TYPES = ['current', 'savings', 'foreign']


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phoneNumber = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.slug


class Wallet(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    type = models.CharField(max_length=100, default='current')
    limit = models.IntegerField(default=100000)
    amount = models.IntegerField(default=0)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    isActive = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    deactivatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.customer.phoneNumber}-{self.type}")
        super(Wallet, self).save(*args, **kwargs)

    # Create a new wallet for a customer
    @classmethod
    def create_wallet(cls, customer, wallet_type):
        if wallet_type in AVAILABLE_WALLET_TYPES:
            wallet_slug = slugify(f"{customer.phoneNumber}-{wallet_type}")
            new_wallet = cls(customer=customer, type=wallet_type, slug=wallet_slug)
            new_wallet.save()
            return new_wallet
        else:
            raise ValueError("Invalid wallet type")

    # Deposit money into the wallet
    def deposit(self, amount):
        self.amount += amount
        self.save()

        # Create a transaction for this deposit
        Transaction.create_transaction(wallet=self, type='deposit', amount=amount, beneficiary=self.customer.phoneNumber)

    # Withdraw money from the wallet
    def withdraw(self, amount):
        if self.amount >= amount:
            self.amount -= amount
            self.save()

            # Create a transaction for this withdrawal
            Transaction.create_transaction(wallet=self, type='withdraw', amount=amount, beneficiary=self.customer.phoneNumber)
        else:
            raise ValueError("Insufficient funds")

    # Transfer money to another wallet
    def transfer(self, amount, receiver_wallet):
        if self.amount >= amount:
            # Deduct from sender
            self.amount -= amount
            self.save()

            # Add to receiver
            receiver_wallet.amount += amount
            receiver_wallet.save()

            # Create transaction for sender and receiver
            Transaction.create_transaction(wallet=self, type='transfer-out', amount=amount, beneficiary=receiver_wallet.customer.phoneNumber)
            Transaction.create_transaction(wallet=receiver_wallet, type='transfer-in', amount=amount, beneficiary=self.customer.phoneNumber)
        else:
            raise ValueError("Insufficient funds")


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    amount = models.IntegerField()
    beneficiary = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.wallet.customer.phoneNumber}-{self.type}-{self.date}-{uuid.uuid4()}")
        super(Transaction, self).save(*args, **kwargs)

    # Create a transaction for any wallet activity
    @classmethod
    def create_transaction(cls, wallet, type, amount, beneficiary):
        transaction = cls(wallet=wallet, type=type, amount=amount, beneficiary=beneficiary)
        transaction.save()
        return transaction
