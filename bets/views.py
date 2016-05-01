from django.shortcuts import render, get_object_or_404
from .models import BinaryBet


def index(request):
    all_binary_bets = BinaryBet.objects.all()
    return render(request, 'index.html', {'all_binary_bets': all_binary_bets})


def bets(request, prim_key):
    bet = get_object_or_404(BinaryBet, prim_key=prim_key)
    return render(request, 'bets.html', {'bet': bet})
