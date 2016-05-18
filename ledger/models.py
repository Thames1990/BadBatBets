from django.db import models

from .util import sum_credit_debit
from bets.util import pkgen


class Account(models.Model):
    types = [
        ('p', 'Person'),
        ('b', 'Bet'),
        ('o', 'Other'),
    ]

    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=64)
    type = models.CharField(max_length=1, choices=types)
    balance = models.IntegerField(default=0)

    def compute_balance(self):
        credits = self.credit_set.all()
        debits = self.debit_set.all()
        self.balance = sum_credit_debit(credits, debits)

    def __str__(self):
        return self.get_type_display() + ": " + self.name


class Transaction(models.Model):

    transaction_id = models.PositiveIntegerField(default=pkgen, primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField()


class Credit(models.Model):

    transaction = models.ForeignKey(Transaction)
    account = models.ForeignKey(Account)
    amount = models.PositiveIntegerField()


class Debit(models.Model):

    transaction = models.ForeignKey(Transaction)
    account = models.ForeignKey(Account)
    amount = models.PositiveIntegerField()
