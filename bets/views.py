from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from .models import PlacedChoiceBet, PlacedDateBet, ChoiceBet, DateBet
from .forms import DateBetCreationForm
from .util import user_can_place_bet, get_bet, generate_index, place_bet_transaction
from ledger.exceptions import InsufficientFunds
from profiles.util import user_authenticated


def index_view(request):
    if not user_authenticated(request.user):
        raise PermissionDenied()

    index = generate_index(request.user)
    return render(request, 'bets/index.html', {
        'choice_bets': index['choice_bets']['available'],
        'placed_choice_bets': index['choice_bets']['placed'],
        'date_bets': index['date_bets']['available'],
        'placed_date_bets': index['date_bets']['placed'],
        'user': request.user
    })


def bet_view(request, prim_key):
    if user_authenticated(request.user):
        bet = get_bet(prim_key)
        if bet is not None:
            if isinstance(bet, ChoiceBet):
                return render(request, 'bets/bets.html', {
                    'choice_bet': bet,
                    'user_can_place_bet': user_can_place_bet(request.user, bet)
                })
            elif isinstance(bet, DateBet):
                return render(request, 'bets/bets.html', {
                    'date_bet': bet,
                    'user_can_place_bet': user_can_place_bet(request.user, bet)
                })
    else:
        raise Http404()


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
        choice.picks += 1
    else:
        placed_bet = PlacedDateBet(
            placed_by=placed_by,
            placed_on=bet,
            placed=placed,
            placed_date=request.POST['date'],
        )

    placed_bet.save()
    return HttpResponseRedirect(reverse('bets:index'))


def create_date_bet(request):
    if not user_authenticated(request.user):
        raise PermissionDenied()

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
