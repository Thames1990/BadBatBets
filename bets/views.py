from django.http import HttpResponse
from .models import BinaryBet


def index(request):
    all_binary_bets = BinaryBet.objects.all()
    html = ''
    for binary_bet in all_binary_bets:
        url = str(binary_bet.prim_key) + '/'
        html += '<a href="' + url + '">' + binary_bet.name + '</a><br>'
    return HttpResponse(html)


def bets(request, prim_key):
    return HttpResponse("<h2>Bet " + str(prim_key) + "</h2>")
