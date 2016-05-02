from django.http import Http404
from django.shortcuts import get_object_or_404, render

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
        bet = get_object_or_404(BinaryBet, prim_key=prim_key)
        choice = request.POST['choice']
        placed_amount = 5000
        chose_alternative = "alternative" in choice
        placed_bet = PlacedBinaryBet(
            placed_on=bet,
            placed_by=request.user.profile,
            placed_amount=1000,
            chose_alternative=chose_alternative
        )
        placed_bet.save()

        all_binary_bets = BinaryBet.objects.all()
        all_placed_bets = PlacedBinaryBet.objects.all()
        bet_on = bet.alternative_option if chose_alternative else bet.null_option
        context = {
            'all_binary_bets': all_binary_bets,
            'all_placed_bets': all_placed_bets,
            'bet_message': "Successfully bet " + str(placed_amount) + " on " + bet_on + " for" + bet.name
        }
        return render(request, 'index.html', context)
        # return HttpResponseRedirect(reverse('bets:binary_bet', args=(bet.prim_key,)))
    else:
        return render(request, 'profiles/login.html')
