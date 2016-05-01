from django.http import Http404
from django.shortcuts import render
from .models import BinaryBet


def index(request):
    all_binary_bets = BinaryBet.objects.all()
    return render(request, 'bets/index.html', {'all_binary_bets': all_binary_bets})


def bets(request, prim_key):
    try:
        bet = BinaryBet.objects.get(prim_key=prim_key)
    except BinaryBet.DoesNotExist:
        raise Http404("Bet doesn't exist")
    return render(request, 'bets/bets.html', {'bet': bet})
