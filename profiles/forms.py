from django import forms

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Profile, Feedback
from ledger.models import Account, Transaction, Credit, Debit


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': '30 characters or fewer. Letters, digits and @/./+/-/_ only.'
            }),
        }
        # TODO Update palceholders

    def clean_username(self):
        return self.cleaned_data.get('username').lower()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')

        if email and User.objects.filter(email=email).exclude(username=username).count():
            raise forms.ValidationError(
                "This email address is already in use. Please supply a different email address.", code='email_in_use')
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


class PaymentForm(forms.Form):
    type = forms.ChoiceField(choices=[('d', 'Deposit'), ('w', 'Withdrawal')])
    account = forms.ModelChoiceField(queryset=User.objects.all())
    amount = forms.IntegerField(min_value=0)

    def clean_account(self):
        account = self.cleaned_data['account'].profile.account

        if not account.type == 'p':
            raise forms.ValidationError("Funds can only be deposited in personal accounts.",
                                        code='deposit_account_not_personal')

        return account

    def clean_amount(self):
        amount = self.cleaned_data['amount']

        if amount <= 0:
            raise forms.ValidationError(
                "This email address is already in use. Please supply a different email address.",
                code='deposit_amount_not_positive')

        if self.cleaned_data['type'] == 'w':
            account = self.cleaned_data['account']
            if account.compute_balance() < amount:
                raise forms.ValidationError("Insufficient funds.", code='insuficcient_funds')

        return self.cleaned_data['amount']

    def save(self, authorised, commit=True):
        user_account = self.cleaned_data['account']
        amount = self.cleaned_data['amount']

        if self.cleaned_data['type'] == 'w':
            system_account = Account.objects.get(name='withdrawal', type='o')
            if amount > 1:
                # TODO Find a transaction description convention
                description = "Wihtdrawal for " + str(amount) + " points \n Authorised by: " + str(authorised)
            else:
                description = "Wihtdrawal for " + str(amount) + " point \n Authorised by: " + str(authorised)

            transaction = Transaction(description=description)
            credit = Credit(transaction=transaction, account=system_account, amount=amount)
            debit = Debit(transaction=transaction, account=user_account, amount=amount)
        else:
            system_account = Account.objects.get(name='deposit', type='o')
            if amount > 1:
                description = "Deposit for " + str(amount) + " points \n Authorised by: " + str(authorised)
            else:
                description = "Deposit for " + str(amount) + " point \n Authorised by: " + str(authorised)

            transaction = Transaction(description=description)
            credit = Credit(transaction=transaction, account=user_account, amount=amount)
            debit = Debit(transaction=transaction, account=system_account, amount=amount)

        transaction.save(commit)
        credit.save(commit)
        debit.save(commit)

        user_account.compute_balance()
        system_account.compute_balance()

        return transaction


class FeedbackForm(forms.Form):
    feedback = forms.CharField(required=True, widget=forms.Textarea)

    def save(self, user, commit=True):
        assert isinstance(user, User)
        saved_feedback = Feedback(provided_by=user, feedback=self.cleaned_data['feedback'])
        saved_feedback.save(commit)

        return saved_feedback
