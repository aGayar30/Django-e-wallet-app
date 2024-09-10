from typing import Iterable
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
import uuid


class Customer(models.Model):
    user = models.OneToOneField(User,  null=True, on_delete=models.CASCADE)  # Link to Django User model
    name = models.CharField(max_length=100)
    phoneNumber = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=255,default='password')
    phoneNumber = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.slug




class Wallet(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE) #cascade so that if there is no person, there will be no wallet
    type = models.CharField(max_length=100, default='current')
    limit = models.IntegerField(default=100000)
    amount = models.IntegerField(default=0)
    slug = models.SlugField(max_length=255, unique=True,blank=True,null=True)
    isActive = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    deactivatedAt = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Create a slug based on customer name and wallet type
        if not self.slug:
            self.slug = slugify(f"{self.customer.phoneNumber}-{self.type}")
        super(Wallet, self).save(*args, **kwargs)

    def __str__(self):
        return self.slug
    

class transactions(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    amount = models.IntegerField()
    benificiary = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Use UUID for ensuring uniqueness
            self.slug = slugify(f"{self.wallet.customer.phoneNumber}-{self.type}-{self.date}-{uuid.uuid4()}")
        super(transactions, self).save(*args, **kwargs)

    def __str__(self):
        return self.slug

