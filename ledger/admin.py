from django.contrib import admin

from .models import Account, Credit, Debit, Transaction


class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'balance')


class CreditAdmin(admin.ModelAdmin):
    list_display = ('account', 'amount')


class DebitAdmin(admin.ModelAdmin):
    list_display = ('account', 'amount')


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', "description")


admin.site.register(Account, AccountAdmin)
admin.site.register(Credit, CreditAdmin)
admin.site.register(Debit, DebitAdmin)
admin.site.register(Transaction, TransactionAdmin)
