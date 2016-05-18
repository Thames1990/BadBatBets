from django.db import models


class Account(models.Model):
    types = [
        ('p', 'Person'),
        ('b', 'Bet'),
        ('o', 'Other'),
    ]

    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=64)


class Transaction(models.Model):
    types = [
        ('c', 'Credit'),
        ('d', 'Debit'),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=64)
    description = models.TextField()
    type = models.CharField(max_length=1, choices=types)
    account = models.ForeignKey(Account)
