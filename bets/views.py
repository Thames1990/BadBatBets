from django.http import HttpResponse
from django.shortcuts import render
from .models import BinaryBet


def index(request):
    all_binary_bets = BinaryBet.objects.all()
    context = {'all_binary_bets': all_binary_bets}
    return render(request, 'bets/index.html', context)


def bets(request, prim_key):
    return HttpResponse("<h2>Bet " + str(prim_key) + "</h2>")
