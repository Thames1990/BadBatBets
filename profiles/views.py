from django.shortcuts import render, redirect
from django.http import HttpResponse


def landing(request):
    if request.user.is_authenticated():
        redirect('profiles:profile')
    else:
        return render(request, 'profiles/landing.html', {})


def profile(request):
    if request.user.is_authenticated():
        return HttpResponse("Logged in!")
    else:
        return redirect('profiles:login')


def login(request):
    if request.user.is_authenticated():
        return redirect('profiles:profile')
    else:
        return HttpResponse("Login Page")
