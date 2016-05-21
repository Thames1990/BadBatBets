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
        cre = self.credit_set.all()
        deb = self.debit_set.all()
        self.balance = sum_credit_debit(cre, deb)
        return self.balance

    def __str__(self):
        return self.get_type_display() + ": " + self.name


class Transaction(models.Model):

    transaction_id = models.PositiveIntegerField(default=pkgen, primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return str(self.transaction_id)


class Credit(models.Model):

    transaction = models.ForeignKey(Transaction)
    account = models.ForeignKey(Account)
    amount = models.PositiveIntegerField()

    def __lt__(self, other):
        return self.transaction.timestamp < other.transaction.timestamp

    def __str__(self):
        return self.transaction.__str__()


class Debit(models.Model):

    transaction = models.ForeignKey(Transaction)
    account = models.ForeignKey(Account)
    amount = models.PositiveIntegerField()

    def __lt__(self, other):
        return self.transaction.timestamp < other.transaction.timestamp

    def __str__(self):
        return self.transaction.__str__()
