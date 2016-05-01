from django.http import Http404
from django.shortcuts import render, get_object_or_404
from .models import BinaryBet, PlacedBinaryBet


def index(request):
    if request.user.is_authenticated():
        all_binary_bets = BinaryBet.objects.all()
        all_placed_bets = PlacedBinaryBet.objects.all()
        context = {
            'all_binary_bets': all_binary_bets,
            'all_placed_bets': all_placed_bets
        }
        return render(request, 'index.html', context)
    else:
        return render(request, 'profiles/login.html')


def binary_bet(request, prim_key):
    if request.user.is_authenticated():
        try:
            bet = BinaryBet.objects.get(prim_key=prim_key)
        except BinaryBet.DoesNotExist:
            try:
                placed_bet = PlacedBinaryBet.objects.get(prim_key=prim_key)
            except PlacedBinaryBet.DoesNotExist:
                raise Http404("Neither a binary bet nor a placed binary bet with id:" + str(prim_key) + " does exist.")
            return render(request, 'placed_binary_bet.html', {'placed_bet': placed_bet})
        return render(request, 'binary_bet.html', {'bet': bet})
    else:
        return render(request, 'profiles/login.html')


def bet_on_binary_bet(request, prim_key):
    if request.user.is_authenticated():
        return render(request, 'index.html')
    else:
        return render(request, 'profiles/login.html')
