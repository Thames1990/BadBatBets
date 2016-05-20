from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponseNotFound

from .forms import SignupForm, LoginForm, DepositForm
from ledger.util import create_table


def landing(request):
    if request.user.is_authenticated():
        return redirect('profiles:profile')
    else:
        return render(request, 'profiles/landing.html', {})


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
        return redirect('profiles:profile')

    args = {}
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('profiles:profile')
    else:
        form = LoginForm()

    args['form'] = form
    return render(request, 'profiles/login.html', args)


def logout_user(request):
    logout(request)
    return render(request, 'profiles/login.html', {
                'message': "Logout Successfull"
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


def change_password(request):
    if not request.user.is_authenticated():
        return redirect(login_user)

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


def transactions(request):
    if not request.user.is_authenticated():
        return redirect(login_user)

    cre = request.user.profile.account.credit_set.all()
    deb = request.user.profile.account.debit_set.all()

    args = {'table': create_table(cre, deb)}

    return render(request, 'profiles/transactions.html', args)


def deposit(request):
    if not request.user.is_authenticated() or not request.user.is_superuser:
        return HttpResponseNotFound()

    args = {}

    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            form.save(authorised=request.user)
    else:
        form = DepositForm()

    args['form'] = form

    return render(request, 'profiles/deposit.html', args)

