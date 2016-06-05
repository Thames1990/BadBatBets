import logging
from datetime import datetime

from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect

from .forms import ChoiceBetCreationForm, DateBetCreationForm
from .models import PlacedChoiceBet, PlacedDateBet, ChoiceBet, DateBet
from .util import user_can_place_bet, get_bet, get_choice, generate_index, place_bet_transaction, resolve_bet
from ledger.exceptions import InsufficientFunds
from profiles.util import user_authenticated

logger = logging.getLogger(__name__)


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
        messages.info(request, "You're not authenticated. Please get in contact with an administrator.")
        if not request.user.is_anonymous():
            logger.info("Unverified user " + request.user.username + " tried to view index page.")
            return redirect('profiles:profile')
        raise PermissionDenied


def bet_view(request, prim_key):
    if user_authenticated(request.user):
        bet = get_bet(prim_key)
        if bet is not None:
            pot_size = bet.account.pot_size()
            if isinstance(bet, ChoiceBet):
                placed_bet = None
                try:
                    placed_bet = bet.placedchoicebet_set.get(placed_by=request.user.profile)
                except PlacedChoiceBet.DoesNotExist:
                    pass
                return render(request, 'bets/bets.html', {
                    'choice_bet': bet,
                    'user_can_place_bet': user_can_place_bet(request.user, bet),
                    'placed_bet': placed_bet,
                    'pot_size': pot_size
                })
            elif isinstance(bet, DateBet):
                placed_bet = None
                try:
                    placed_bet = bet.placeddatebet_set.get(placed_by=request.user.profile)
                except PlacedDateBet.DoesNotExist:
                    pass
                return render(request, 'bets/bets.html', {
                    'date_bet': bet,
                    'user_can_place_bet': user_can_place_bet(request.user, bet),
                    'placed_bet': placed_bet,
                    'pot_size': pot_size
                })
            else:
                warning_message = "Bets with type " + type(bet).__name__ + " aren't handled yet."
                logger.warning(warning_message)
                messages.warning(request, warning_message)
                raise Http404
        else:
            messages.info(request, "Bet with primary key " + str(prim_key) + " does not exist.")
            raise Http404
    else:
        messages.info(request, "You're not authenticated. Please get in contact with an administrator.")
        if not request.user.is_anonymous():
            logger.warning(
                "Unverified user " + request.user.username + " tried to take a look at bet with primary key " +
                str(prim_key) + ".")
            return redirect('profiles:profile')
        raise PermissionDenied


def place_bet(request, prim_key):
    if user_authenticated(request.user):
        bet = get_bet(prim_key)
        if bet is None:
            messages.error(request, "No bet with primary key " + str(prim_key) + " was found.")
            raise Http404
        elif not user_can_place_bet(user=request.user, bet=bet):
            messages.info(request, "You already placed a bet on " + bet.name + ".")
            raise Http404
        else:
            placed_by = request.user.profile
            placed = int(request.POST['placed'])

            try:
                place_bet_transaction(profile=placed_by, bet=bet, amount=placed)
            except InsufficientFunds:
                messages.info(request, "Insufficient funds. Your accounts balance is " +
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
                logger.warning("Bets with type " + type(bet).__name__ + " are not handled yet.")
                messages.warning(request, "Bets with type " + type(bet).__name__ + " are not handled yet.")
                raise Http404

            messages.success(request, "Succesfully placed " + str(placed) + " points on" + str(bet) + ".")
            return HttpResponseRedirect(reverse('bets:bet', args={bet.prim_key}))
    else:
        messages.info(request, "You're not authenticated. Please get in contact with an administrator.")
        if not request.user.is_anonymous():
            logger.warning("Unverified user " + request.user.username + " tried to place on bet with primary key " +
                           str(prim_key) + ".")
            return redirect('profiles:profile')
        raise PermissionDenied


def resolve_bet_view(request, prim_key):
    if user_authenticated(request.user):
        bet = get_bet(prim_key)
        if bet is None:
            messages.error(request, "No bet with primary key " + str(prim_key) + " was found.")
            raise Http404
        else:
            if isinstance(bet, ChoiceBet):
                winning_choice = request.POST['choice']
                winning_choice = get_choice(winning_choice)
                if winning_choice is not None:
                    resolve_bet(bet, winning_choice)
                    messages.success(request, "Succesfully resolved " + str(bet) + ".")
                    return HttpResponseRedirect(reverse('bets:bet', args={bet.prim_key}))
                else:
                    messages.error(
                        request,
                        "Choice with description " + winning_choice + " for bet " + bet + " does not exist."
                    )
                    raise Http404
            elif isinstance(bet, DateBet):
                winning_date = datetime.strptime(request.POST['date'], '%Y-%m-%d').date()
                if winning_date is not None:
                    resolve_bet(bet, winning_date)
                    messages.success(request, "Succesfully resolved " + str(bet) + ".")
                    return HttpResponseRedirect(reverse('bets:bet', args={bet.prim_key}))
                else:
                    messages.error(request, "Date does not exist.")
                    raise Http404
    else:
        messages.info(request, "You're not authenticated. Please get in contact with an administrator.")
        if not request.user.is_anonymous():
            logger.warning("Unverified user " + request.user.username + " tried to resolve bet with primary key " +
                           str(prim_key) + ".")
            return redirect('profiles:profile')
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

                messages.success(request, "Succesfully created " + str(bet) + ".")
                return HttpResponseRedirect(reverse('bets:bet', args={bet.prim_key}))
        else:
            form = ChoiceBetCreationForm()

        return render(request, 'bets/create_choice_bet.html', {'form': form})
    else:
        messages.info(request, "You're not authenticated. Please get in contact with an administrator.")
        if not request.user.is_anonymous():
            logger.warning("Unverified user " + request.user.username + " tried to place create a choice bet.")
            return redirect('profiles:profile')
        raise PermissionDenied


def create_date_bet(request):
    if user_authenticated(request.user):
        if request.method == 'POST':
            form = DateBetCreationForm(data=request.POST)
            if form.is_valid():
                bet = form.save(request.user.profile)
                messages.success(request, "Succesfully created " + str(bet) + ".")
                return HttpResponseRedirect(reverse('bets:bet', args={bet.prim_key}))
        else:
            form = DateBetCreationForm()

        return render(request, 'bets/create_date_bet.html', {'form': form})
    else:
        messages.info(request, "You're not authenticated. Please get in contact with an administrator.")
        if not request.user.is_anonymous():
            logger.warning("Unverified user " + request.user.username + " tried to place create a date bet.")
            return redirect('profiles:profile')
        raise PermissionDenied
