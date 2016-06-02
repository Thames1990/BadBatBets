from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect

from .forms import SignupForm, LoginForm, PaymentForm
from ledger.util import create_table
from bets.util import generate_profile_resolved_bet


def landing(request):
    if request.user.is_authenticated():
        return redirect('bets:index')
    else:
        return render(request, 'profiles/landing.html')


@login_required
def profile(request):
    resolved_bets = generate_profile_resolved_bet(request.user.profile)
    return render(request, 'profiles/profile.html', {
        'resolved_placed_choice_bets': resolved_bets['resolved_placed_choice_bets'],
        'resolved_placed_date_bets': resolved_bets['resolved_placed_date_bets'],
    })


def login_user(request):
    if request.user.is_authenticated():
        return redirect('bets:index')
    else:
        if request.method == 'POST':
            form = LoginForm(data=request.POST)
            if form.is_valid():
                login(request, form.get_user())
                return redirect('bets:index')
        else:
            form = LoginForm()

        return render(request, 'profiles/login.html', {'form': form})


@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "Logout successful")
    return render(request, 'profiles/login.html')


def signup(request):
    if request.user.is_authenticated():
        return redirect('bets:index')
    else:
        if request.method == 'POST':
            form = SignupForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect(login_user)
        else:
            form = SignupForm()

        return render(request, 'profiles/signup.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(login_user)

    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'profiles/change_password.html', {'form': form})


def transactions(request):
    if request.user.is_authenticated():
        credit = request.user.profile.account.credit_set.all()
        debit = request.user.profile.account.debit_set.all()

        return render(request, 'profiles/transactions.html', {
            'table': create_table(credit, debit)
        })
    else:
        messages.error(request, "You're not authenticated. Please get in contact with an administrator.")
        raise PermissionDenied


def payment(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            form = PaymentForm(request.POST)
            if form.is_valid():
                form.save(authorised=request.user)
        else:
            form = PaymentForm()

        return render(request, 'profiles/payment.html', {'form': form})
    else:
        messages.error(request, "You're not authenticated. Please get in contact with an administrator.")
        raise PermissionDenied


def general_terms_and_conditions_view(request):
    return render(request, 'profiles/general_terms_and_conditions.html')


def privacy_policy_view(request):
    return render(request, 'profiles/privacy_policy.html')
