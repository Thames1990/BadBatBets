from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound

from .forms import SignupForm, LoginForm, PaymentForm
from ledger.util import create_table


def landing(request):
    if request.user.is_authenticated():
        return redirect('bets:index')
    else:
        return render(request, 'profiles/landing.html', {})


@login_required
def profile(request):
    if request.user.is_authenticated():
        return render(request, 'profiles/profile.html', {
            'user': request.user,
            'profile': request.user.profile
        })
    else:
        return redirect(login_user)


def login_user(request):
    if request.user.is_authenticated():
        return redirect('bets:index')
    else:
        args = {}
        if request.method == 'POST':
            form = LoginForm(data=request.POST)
            # TODO fix "This field is required" even if data is available
            # TODO /login and /profile/login differ
            if form.is_valid():
                login(request, form.get_user())
                return redirect('bets:index')
        else:
            # TODO Fix "blank" login button step
            form = LoginForm()

        args['form'] = form
        return render(request, 'profiles/login.html', args)


@login_required
def logout_user(request):
    logout(request)
    return render(request, 'profiles/login.html', {
        'message': "Logout Successful"
    })


def signup(request):
    args = {}
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(login_user)
    else:
        form = SignupForm()

    args['form'] = form
    return render(request, 'profiles/signup.html', args)


@login_required
def change_password(request):
    if request.user.is_authenticated():
        args = {}
        if request.method == 'POST':
            form = PasswordChangeForm(request.user, data=request.POST)
            if form.is_valid():
                form.save()
                return redirect(login_user)

        else:
            form = PasswordChangeForm(request.user)

        args['form'] = form
        return render(request, 'profiles/change_password.html', args)
    else:
        return redirect(login_user)


@login_required
def transactions(request):
    if request.user.is_authenticated():
        credit = request.user.profile.account.credit_set.all()
        debit = request.user.profile.account.debit_set.all()

        return render(request, 'profiles/transactions.html', {
            'table': create_table(credit, debit)
        })
    else:
        return redirect(login_user)


@login_required
def payment(request):
    if not request.user.is_authenticated() or not request.user.is_superuser:
        return HttpResponseNotFound()

    args = {}

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save(authorised=request.user)
    else:
        form = PaymentForm()

    args['form'] = form

    return render(request, 'profiles/payment.html', args)


def general_terms_and_conditions_view(request):
    return render(request, 'profiles/general_terms_and_conditions.html',
                  {'accepted': request.user.profile.accepted_agb})


def privacy_policy_view(request):
    return render(request, 'profiles/privacy_policy.html', {
        'accepted': request.user.profile.accepted_privacy_policy
    })
