from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect

from django.shortcuts import render, redirect

from .forms import ChoiceBetCreationForm, DateBetCreationForm
from .models import PlacedChoiceBet, PlacedDateBet, ChoiceBet, DateBet
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
        })
    else:
        messages.error(request, "You're not authenticated. Please get in contact with an administrator.")
        raise PermissionDenied


def bet_view(request, prim_key):
    if user_authenticated(request.user):
        bet = get_bet(prim_key)
        if bet is not None:
            if isinstance(bet, ChoiceBet):
                placed_bet = None
                try:
                    placed_bet = bet.placedchoicebet_set.get(placed_by=request.user.profile)
                except PlacedChoiceBet.DoesNotExist:
                    pass
                return render(request, 'bets/bets.html', {
                    'choice_bet': bet,
                    'user_can_place_bet': user_can_place_bet(request.user, bet),
                    'placed_bet': placed_bet
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
        raise PermissionDenied


def place_bet(request, prim_key):
    if user_authenticated(request.user):
        bet = get_bet(prim_key)
        if bet is None:
            messages.error(request, "No bet with primary key " + str(prim_key) + " was found.")
            raise Http404
        elif not user_can_place_bet(user=request.user, bet=bet):
            messages.error(request, "You already placed a bet on " + bet.name + ".")
            raise Http404
        else:
            placed_by = request.user.profile
            placed = int(request.POST['placed'])

            try:
                place_bet_transaction(profile=placed_by, bet=bet, amount=placed)
            except InsufficientFunds:
                print(request.user.profile.account.balance)
                messages.error(request, "Insufficient funds. Your accounts balance is " +
                               str(request.user.profile.account.balance) + " points and you wanted to bet " +
                               str(placed) + " points.")
                return HttpResponseRedirect(reverse('bets:bet', args={bet.prim_key}))

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
                messages.error(request, "Bets with type " + type(bet).__name__ + " are not handled yet.")
                raise Http404

            return HttpResponseRedirect(reverse('bets:index'))
    else:
        messages.error(request, "You're not authenticated. Please get in contact with an administrator.")
        raise PermissionDenied


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
        messages.error(request, "You're not authenticated. Please get in contact with an administrator.")
        raise PermissionDenied


def create_choice_bet(request):
    if user_authenticated(request.user):
        if request.method == 'POST':
            form = ChoiceBetCreationForm(request.POST)
            if form.is_valid():
                try:
                    bet = form.save(request)
                except ValidationError:
                    messages.error(request, "Invalid choice descriptions. Use distinct and non empty descriptions.")
                    return redirect('bets:create_choice_bet')

                return HttpResponseRedirect(reverse('bets:bet', args={bet.prim_key}))
        else:
            form = ChoiceBetCreationForm()

        return render(request, 'bets/create_choice_bet.html', {'form': form})
    else:
        messages.error(request, "You're not authenticated. Please get in contact with an administrator.")
        raise PermissionDenied
