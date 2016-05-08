from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.utils import timezone

from .models import Bet, ChoiceBet, Choice


def index_view(request):
    if request.user.is_authenticated():
        # TODO exclude forbidden bets
        # TODO include self created bets without publish date
        bets = Bet.objects \
            .filter(resolved=False) \
            .filter(published_date__isnull=False) \
            .filter(published_date__lte=timezone.now()) \
            .exclude(choicebet__chosen__belongs_to__in=request.user.profile.bet_set.all())
        choice_bets = ChoiceBet.objects.all()
        context = {
            'bets': bets,
            'choice_bets': choice_bets,
        }
        return render(request, 'bets/index.html', context)
    else:
        return render(request, 'profiles/login.html')


def bet_view(request, prim_key):
    # TODO filter for forbidden bets
    if request.user.is_authenticated():
        try:
            bet = Bet.objects.get(prim_key=prim_key)
        except Bet.DoesNotExist:
            try:
                choice_bet = ChoiceBet.objects.get(prim_key=prim_key)
            except ChoiceBet.DoesNotExist:
                raise Http404("Neither a binary bet nor a placed binary bet with id:" + str(prim_key) + " does exist.")
            else:
                return render(request, 'bets/bets.html', {'choice_bet': choice_bet})
        else:
            return render(request, 'bets/bets.html', {'bet': bet})
    else:
        return render(request, 'profiles/login.html')


def choice_bet_view(request, prim_key):
    if request.user.is_authenticated():
        bet = get_object_or_404(Bet, prim_key=prim_key)
        try:
            choice = bet.choice_set.get(description=request.POST['choice'])
        except (KeyError, Choice.DoesNotExist):
            return render(request, 'bets/bets.html', {'bet': bet})
        else:
            choice_bet = ChoiceBet(
                placed_by=request.user.profile,
                placed_on=bet,
                chosen=choice,
                placed=request.POST['placed'],
            )
            choice_bet.save()
            return HttpResponseRedirect(reverse('bets:index'))
    else:
        return render(request, 'profiles/login.html')
