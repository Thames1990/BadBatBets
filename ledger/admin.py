from django.contrib import admin

from .models import Account, Credit, Debit, Transaction


admin.site.register(Account)
admin.site.register(Credit)
admin.site.register(Debit)
admin.site.register(Transaction)
