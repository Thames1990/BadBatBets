from django import forms

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import ugettext_lazy as _

from .models import Profile
from ledger.models import Account, Transaction, Credit, Debit


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_username(self):
        return self.cleaned_data.get('username').lower()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')

        if email and User.objects.filter(email=email).exclude(username=username).count():
            raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
        return email

    def save(self, commit=True):
        user = super(SignupForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()

        account = Account(name=user.username, type='p')
        account.save(commit)
        profile = Profile(user=user, account=account)
        profile.save(commit)
        return user


class LoginForm(AuthenticationForm):
    def clean_username(self):
        return self.cleaned_data.get('username').lower()


class DepositForm(forms.Form):
    account = forms.ModelChoiceField(queryset=User.objects.all())
    amount = forms.IntegerField()

    def clean_account(self):
        account = self.cleaned_data['account'].profile.account

        if not account.type == 'p':
            raise forms.ValidationError(
                _("Funds can only be deposited in personal accounts."),
                code='deposit_account_not_personal',
            )

        return account

    def clean_amount(self):
        if self.cleaned_data['amount'] <= 0:
            raise forms.ValidationError(
                _("This email address is already in use. Please supply a different email address."),
                code='deposit_amount_not_positive',
            )

        return self.cleaned_data['amount']

    def save(self, authorised, commit=True):
        deposit_account = Account.objects.get(name='deposit')
        user_account = self.cleaned_data['account']
        description = "Deposit authorised by: " + str(authorised)

        transaction = Transaction(description=description)
        transaction.save(commit)
        credit = Credit(transaction=transaction, account=user_account, amount=self.cleaned_data['amount'])
        debit = Debit(transaction=transaction, account=deposit_account, amount=self.cleaned_data['amount'])
        credit.save(commit)
        debit.save(commit)

        return transaction
