from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login


def landing(request):
    if request.user.is_authenticated():
        redirect('profiles:profile')
    else:
        return render(request, 'profiles/landing.html', {})


def profile(request):
    if request.user.is_authenticated():
        return HttpResponse("Logged in!")
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
