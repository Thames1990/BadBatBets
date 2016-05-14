from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm

from .forms import SignupForm


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


def login_page(request):
    if request.user.is_authenticated():
        return redirect('profiles:profile')
    else:
        return render(request, 'profiles/login.html')


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('profiles:profile')
            else:
                return render(request, 'profiles/login.html', {
                    'error_message': "Account inactive"
                })
        else:
            return render(request, 'profiles/login.html', {
                    'error_message': "Unknown User"
                })
    else:
        return login_page(request)


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
