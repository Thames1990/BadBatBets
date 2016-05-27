from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from .models import PlacedChoiceBet, PlacedDateBet, ChoiceBet, DateBet
from .forms import DateBetCreationForm
from .util import filter_visible_bets, user_can_place_bet, get_bet
from ledger.util import place_bet_transaction
from ledger.exceptions import InsufficientFunds
from profiles.util import user_authenticated


def index_view(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            if request.POST.get('agb'):
                request.user.profile.accepted_agb = True
                request.user.profile.save()
            elif request.POST.get('privacy_policy'):
                request.user.profile.accepted_privacy_policy = True
                request.user.profile.save()

        if request.user.profile.accepted_agb and request.user.profile.accepted_privacy_policy:
            choice_bets = ChoiceBet.objects.all()
            placed_choice_bets = request.user.profile.placedchoicebet_set.all()
            date_bets = DateBet.objects.all()
            placed_date_bets = request.user.profile.placeddatebet_set.all()
            return render(request, 'bets/index.html', {
                'choice_bets': filter_visible_bets(choice_bets, request.user.profile),
                'placed_choice_bets': placed_choice_bets,
                'date_bets': filter_visible_bets(date_bets, request.user.profile),
                'placed_date_bets': placed_date_bets,
                'user': request.user
            })
        elif not request.user.profile.accepted_agb:
            return render(request, 'profiles/general_terms_and_conditions.html', {'accepted': False})
        else:
            return render(request, 'profiles/privacy_policy.html', {'accepted': False})
    else:
        return render(request, 'profiles/login.html')


@login_required
def bet_view(request, prim_key):
    if request.user.is_authenticated():
        try:
            choice_bet = ChoiceBet.objects.get(prim_key=prim_key)
        except ChoiceBet.DoesNotExist:
            try:
                date_bet = DateBet.objects.get(prim_key=prim_key)
            except DateBet.DoesNotExist:
                try:
                    placed_choice_bet = PlacedChoiceBet.objects.get(prim_key=prim_key)
                except PlacedChoiceBet.DoesNotExist:
                    try:
                        placed_date_bet = PlacedDateBet.objects.get(prim_key=prim_key)
                    except:
                        raise Http404(
                            "Neither a choice bet nor a date bet with id:" + str(prim_key) + " does exist."
                        )
                    else:
                        return render(request, 'bets/bets.html', {
                            'placed_date_bet': placed_date_bet.placed_on,
                            'user_can_bet': False
                        })
                else:
                    return render(request, 'bets/bets.html', {
                        'choice_bet': placed_choice_bet.placed_on,
                        'user_can_bet': False
                    })
            else:
                return render(request, 'bets/bets.html', {
                    'date_bet': date_bet,
                    'user_can_bet': user_can_place_bet(request.user, date_bet)
                })
        else:
            return render(request, 'bets/bets.html', {
                'choice_bet': choice_bet,
                'user_can_bet': user_can_place_bet(request.user, choice_bet)
            })
    else:
        return render(request, 'profiles/login.html')


def place_bet(request, prim_key):
    bet = get_bet(prim_key)
    if (bet is None) or (not user_can_place_bet(user=request.user, bet=bet)):
        raise Http404(
            # TODO: Do a proper 404...
            _("Foobar")
        )

    placed_by = request.user.profile
    placed = request.POST['placed']

    try:
        place_bet_transaction(user=placed_by, bet=bet, amount=placed)
    except InsufficientFunds:
        # TODO: do something useful here...
        pass

    if isinstance(bet, ChoiceBet):
        choice = bet.choice_set.get(description=request.POST['choice'])
        placed_bet = PlacedChoiceBet(
            placed_by=placed_by,
            placed_on=bet,
            placed=placed,
            chosen=choice
        )
    else:
        placed_bet = PlacedDateBet(
            placed_by=placed_by,
            placed_on=bet,
            placed=placed,
            placed_date=request.POST['date'],
        )

    placed_bet.save()
    return HttpResponseRedirect(reverse('bets:index'))


@login_required
def create_date_bet(request):
    args = {}
    if request.method == 'POST':
        form = DateBetCreationForm(data=request.POST)
        if form.is_valid():
            bet = form.save(request.user.profile)
            return HttpResponseRedirect(reverse('bets:bet', args={bet.prim_key}))
    else:
        form = DateBetCreationForm()

    args['form'] = form

    return render(request, 'bets/create_date_bet.html', args)
