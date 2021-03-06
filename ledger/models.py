from django.db import models

from .util import sum_credit_debit
from bets.util import key_gen


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
        credit = self.credit_set.all()
        debit = self.debit_set.all()
        self.balance = sum_credit_debit(credit, debit)
        self.save()
        return self.balance

    def pot_size(self):
        total = 0
        for credit in self.credit_set.all():
            total += credit.amount
        return total

    def __str__(self):
        return self.get_type_display() + ": " + self.name


class Transaction(models.Model):
    transaction_id = models.PositiveIntegerField(default=key_gen, primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return str(self.transaction_id)


class Credit(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    def __lt__(self, other):
        return self.transaction.timestamp < other.transaction.timestamp

    def __str__(self):
        return self.transaction.__str__()


class Debit(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    def __lt__(self, other):
        return self.transaction.timestamp < other.transaction.timestamp

    def __str__(self):
        return self.transaction.__str__()
