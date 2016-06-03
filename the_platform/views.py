from django.shortcuts import render

from profiles.util import user_authenticated


def error403(request):
    return render(request, 'the_platform/403.html', {
        'user_authenticated': user_authenticated(request.user)
    })


def error404(request):
    return render(request, 'the_platform/404.html', {
        'user_authenticated': user_authenticated(request.user)
    })


def error500(request):
    return render(request, 'the_platform/500.html', {
        'user_authenticated': user_authenticated(request.user)
    })
