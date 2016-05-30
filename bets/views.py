from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render

from .forms import ChoiceBetCreationForm, DateBetCreationForm
from .models import PlacedChoiceBet, PlacedDateBet, ChoiceBet, DateBet, Choice
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
        messages.error(request, "You're not authenticated. Please get in contact with an administrator.")
        raise Http404


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
                messages.error(request, "Bets with type " + type(bet).__name__ + " aren't handled yet.")
                raise Http404
        else:
            messages.error(request, "Bet with primary key " + str(prim_key) + " does not exist.")
            raise Http404
    else:
        messages.error(request, "You're not authenticated. Please get in contact with an administrator.")
        raise Http404


def place_bet(request, prim_key):
    if user_authenticated(request.user):
        bet = get_bet(prim_key)
        if (bet is None) or (not user_can_place_bet(user=request.user, bet=bet)):
            raise Http404
        else:
            placed_by = request.user.profile
            placed = int(request.POST['placed'])

            try:
                place_bet_transaction(profile=placed_by, bet=bet, amount=placed)
            except InsufficientFunds:
                # TODO: Notify the user that he/she doesn't have sufficient funds for the (placed) bet.
                pass

            if isinstance(bet, ChoiceBet):
                choice = bet.choice_set.get(description=request.POST['choice'])
                choice.picks += 1
                choice.save()
                PlacedChoiceBet(
                    placed_by=placed_by,
                    placed_on=bet,
                    placed=placed,
                    chosen=choice
                ).save()
            elif isinstance(bet, DateBet):
                PlacedDateBet(
                    placed_by=placed_by,
                    placed_on=bet,
                    placed=placed,
                    placed_date=request.POST['date'],
                ).save()
            else:
                raise TypeError("Bets with type " + type(bet).__name__ + " are not handled yet.")

            return HttpResponseRedirect(reverse('bets:index'))
    else:
        raise PermissionDenied


# TODO generic create_bet (POST fields?)

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
        raise PermissionDenied


def create_choice_bet(request):
    if user_authenticated(request.user):
        if request.method == 'POST':
            form = ChoiceBetCreationForm(request.POST)

            if form.is_valid():
                bet = form.save(request.user.profile)
                create_choices(request, bet)
                return HttpResponseRedirect(reverse('bets:bet', args={bet.prim_key}))
        else:
            form = ChoiceBetCreationForm()

        return render(request, 'bets/create_choice_bet.html', {'form': form})
    else:
        raise PermissionDenied


def create_choices(request, bet):
    last_choice = False
    choice_number = 1
    while not last_choice:
        choice = request.POST.get("choice_" + str(choice_number))
        if choice is not None:
            Choice(
                belongs_to=bet,
                description=choice
            ).save()

            choice_number += 1
        else:
            last_choice = True
