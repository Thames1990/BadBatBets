from django.shortcuts import render


def error404(request):
    return render(request, 'the_platform/404.html', {
        'request': request
    })
