from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.utils import timezone

from .models import Bet, PlacedBet, Choice, ChoiceBet


def index_view(request):
    if request.user.is_authenticated():
        # TODO exclude forbidden bets
        # TODO include self created bets without publish date
        choice_bets = ChoiceBet.objects \
            .filter(published_date__lte=timezone.now()) \
            .exclude(choices__placedbet__placed_on__in=request.user.profile.bet_set.all())
        placed_bets = PlacedBet.objects.all()
        return render(request, 'bets/index.html', {
            'choice_bets': choice_bets,
            'placed_bets': placed_bets,
            'user': request.user
        })
    else:
        return render(request, 'profiles/login.html')


def bet_view(request, prim_key):
    # TODO Filter for forbidden bets
    # TODO Exclude already bet on
    if request.user.is_authenticated():
        try:
            choice_bet = ChoiceBet.objects.get(prim_key=prim_key)
        except ChoiceBet.DoesNotExist:
            try:
                placed_bet = PlacedBet.objects.get(prim_key=prim_key)
            except PlacedBet.DoesNotExist:
                raise Http404("Neither a binary bet nor a placed binary bet with id:" + str(prim_key) + " does exist.")
            else:
                return render(request, 'bets/bets.html', {'placed_bet': placed_bet})
        else:
            return render(request, 'bets/bets.html', {'choice_bet': choice_bet})
    else:
        return render(request, 'profiles/login.html')


def choice_bet_view(request, prim_key):
    if request.user.is_authenticated():
        choice_bet = get_object_or_404(ChoiceBet, prim_key=prim_key)
        try:
            choice = choice_bet.choices.get(description=request.POST['choice'])
        except (KeyError, Choice.DoesNotExist):
            return render(request, 'bets/bets.html', {'choice_bet': choice_bet})
        else:
            placed_bet = PlacedBet(
                placed_by=request.user.profile,
                placed_on=choice_bet,
                chosen=choice,
                placed=request.POST['placed'],
            )
            placed_bet.save()
            return HttpResponseRedirect(reverse('bets:index'))
    else:
        return render(request, 'profiles/login.html')
