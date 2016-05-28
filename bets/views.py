from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.generic import View

from .models import PlacedChoiceBet, PlacedDateBet, ChoiceBet, DateBet
from .forms import ChoiceBetCreationForm, DateBetCreationForm
from .util import user_can_place_bet, get_bet, generate_index, place_bet_transaction
from ledger.exceptions import InsufficientFunds
from profiles.util import user_authenticated


def index_view(request):
    if user_authenticated(request.user):
        index = generate_index(request.user)
        return render(request, 'bets/index.html', {
            'choice_bets': index['choice_bets']['available'],
            'placed_choice_bets': index['choice_bets']['placed'],
            'date_bets': index['date_bets']['available'],
            'placed_date_bets': index['date_bets']['placed'],
            'user': request.user
        })
    # TODO Readd terms and policy agreement check (updated)
    else:
        raise PermissionDenied()


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
                raise TypeError("Bets with type " + type(bet).__name__ + " are not handled yet.")
        else:
            raise ObjectDoesNotExist("No bet with primary key " + str(prim_key) + " exists.")
    else:
        # TODO Create custom 404 page
        raise Http404()


def place_bet(request, prim_key):
    if user_authenticated(request.user):
        bet = get_bet(prim_key)
        if (bet is None) or (not user_can_place_bet(user=request.user, bet=bet)):
            raise Http404()
        else:
            placed_by = request.user.profile
            # TODO check why this was str
            placed = int(request.POST['placed'])

            try:
                # TODO points aren't withdrawn yet. (At least not saved)
                place_bet_transaction(user=placed_by, bet=bet, amount=placed)
            except InsufficientFunds:
                # TODO: Notify the user that he/she doesn't have sufficient funds for the (placed) bet.
                pass

            if isinstance(bet, ChoiceBet):
                choice = bet.choice_set.get(description=request.POST['choice'])
                placed_bet = PlacedChoiceBet(
                    placed_by=placed_by,
                    placed_on=bet,
                    placed=placed,
                    chosen=choice
                )
                placed_bet.save()
                choice.picks += 1
                choice.save()
            elif isinstance(bet, DateBet):
                placed_bet = PlacedDateBet(
                    placed_by=placed_by,
                    placed_on=bet,
                    placed=placed,
                    placed_date=request.POST['date'],
                )
                placed_bet.save()
            else:
                raise TypeError("Bets with type " + type(bet).__name__ + " are not handled yet.")

            return HttpResponseRedirect(reverse('bets:index'))
    else:
        raise PermissionDenied()


def create_date_bet(request):
    if user_authenticated(request.user):
        if request.method == 'POST':
            form = DateBetCreationForm(data=request.POST)
            if form.is_valid():
                bet = form.save(request.user.profile)
                return HttpResponseRedirect(reverse('bets:bet', args={bet.prim_key}))
        else:
            form = DateBetCreationForm()

        return render(request, 'bets/create_date_bet.html', {'form': form})
    else:
        raise PermissionDenied()


def create_choice_bet(request):
    if request.method == 'POST':
        form = ChoiceBetCreationForm(request.POST)
        if form.is_valid():
            bet = form.save(request.user.profile)
            return HttpResponseRedirect(reverse('bets:bet', args={bet.prim_key}))
    else:
        form = ChoiceBetCreationForm()

    return render(request, 'bets/create_date_bet.html', {'form': form})


class CreateChoiceBet(View):
    form_class = ChoiceBetCreationForm
    template_name = 'bets/create_date_bet.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            # TODO fix save method (commit=False)
            choice_bet = form.save(request.user.profile)
            # TODO insert checks
            choice_bet.save()
