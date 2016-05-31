from django.shortcuts import render


def error404(request):
    return render(request, 'the_platform/404.html')


def error403(request):
    return render(request, 'the_platform/403.html')


def error500(request):
    return render(request, 'the_platform/500.html')
