from django.shortcuts import render, get_object_or_404
from .models import BinaryBet, PlacedBinaryBet


def index(request):
    all_binary_bets = BinaryBet.objects.all()
    all_placed_bets = PlacedBinaryBet.objects.all()
    context = {
        'all_binary_bets': all_binary_bets,
        'all_placed_bets': all_placed_bets
    }
    return render(request, 'index.html', context)


def binary_bet(request, prim_key):
    bet = get_object_or_404(BinaryBet, prim_key=prim_key)
    return render(request, 'binary_bet.html', {'bet': bet})


def placed_binary_bet(request, binary_bet_prim_key_, placed_binary_bet_prim_key):
    bet = get_object_or_404(BinaryBet, prim_key=binary_bet_prim_key_)
    placed_bet = get_object_or_404(PlacedBinaryBet, prim_key=placed_binary_bet_prim_key)
    return render(request, 'placed_binary_bet.html', {'placed_bet': placed_bet})


def bet_on_binary_bet(request, prim_key):
    # TODO Do stuff Markus
    bet = get_object_or_404(BinaryBet, prim_key=prim_key)
    # try:
    #     # Get choice
    # except (KeyError, Choice.DoesNotExist):
    #     return render(request, 'binary_bet.html', {
    #         'bet': bet,
    #         'error_message': "You didn't select a valid choice."
    #     })
    # else:
    #     # Select choice, save stuff and return to site
