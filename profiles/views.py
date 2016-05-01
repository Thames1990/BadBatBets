from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout


def landing(request):
    if request.user.is_authenticated():
        redirect('profiles:profile')
    else:
        return render(request, 'profiles/landing.html', {})


def profile(request):
    if request.user.is_authenticated():
        return render(request, 'profiles/profile.html')
    else:
        return redirect('profiles:login_page')


def login_page(request):
    if request.user.is_authenticated():
        return redirect('profiles:profile')
    else:
        return render(request, 'profiles/login.html')


def login_user(request):
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


def logout_user(request):
    logout(request)
    return render(request, 'profiles/login.html', {
                'message': "Logout Successfull"
            })
