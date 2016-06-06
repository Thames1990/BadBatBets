import logging
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.urlresolvers import reverse, reverse_lazy
from django.forms import SelectDateWidget, SelectMultiple
from django.forms.models import modelform_factory
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic.edit import UpdateView, DeleteView

from .forms import ChoiceBetCreationForm, DateBetCreationForm
from .models import PlacedChoiceBet, PlacedDateBet, ChoiceBet, DateBet, ForbiddenUser
from .util import user_can_place_bet, get_bet, get_placed_bet_for_profile, get_choice, generate_index, \
    place_bet_transaction, resolve_bet
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


@login_required
def bet_view(request, prim_key):
    if user_authenticated(request.user):
        bet = get_bet(prim_key)
        if bet is not None:
            pot_size = bet.account.pot_size()
            placed_bet = get_placed_bet_for_profile(bet, request.user.profile)
            if isinstance(bet, ChoiceBet):
                return render(request, 'bets/bets.html', {
                    'choice_bet': bet,
                    'user_can_place_bet': user_can_place_bet(request.user, bet),
                    'placed_bet': placed_bet,
                    'pot_size': pot_size
                })
            elif isinstance(bet, DateBet):
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


@login_required
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
                transaction = place_bet_transaction(profile=placed_by, bet=bet, amount=placed)
            except InsufficientFunds:
                messages.info(request, "Insufficient funds. Your accounts balance is " +
                              str(request.user.profile.account.balance) + " points and you wanted to bet " +
                              str(placed) + " points.")
                return HttpResponseRedirect(reverse('bets:bet', args={bet.prim_key}))

            if isinstance(bet, ChoiceBet):
                choice = bet.choice_set.get(description=request.POST['choice'])
                choice.picks += 1
                choice.save()
                PlacedChoiceBet.objects.create(
                    placed_by=placed_by,
                    placed_on=bet,
                    placed=placed,
                    chosen=choice,
                    transaction=transaction
                ).save()
            elif isinstance(bet, DateBet):
                PlacedDateBet.objects.create(
                    placed_by=placed_by,
                    placed_on=bet,
                    placed=placed,
                    placed_date=request.POST['date'],
                    transaction=transaction
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


@login_required
def resolve_bet_view(request, prim_key):
    if user_authenticated(request.user):
        bet = get_bet(prim_key)
        if bet is not None:
            if isinstance(bet, ChoiceBet):
                winning_choice = get_choice(request.POST['choice'])
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
                logger.warning("Bets with type " + type(bet).__name__ + " are not handled yet.")
                messages.warning(request, "Bets with type " + type(bet).__name__ + " are not handled yet.")
                raise Http404
        else:
            messages.error(request, "No bet with primary key " + str(prim_key) + " was found.")
            raise Http404
    else:
        messages.info(request, "You're not authenticated. Please get in contact with an administrator.")
        if not request.user.is_anonymous():
            logger.warning("Unverified user " + request.user.username + " tried to resolve bet with primary key " +
                           str(prim_key) + ".")
            return redirect('profiles:profile')
        raise PermissionDenied


@login_required
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

        return render(request, 'bets/choicebet_create_form.html', {'form': form})
    else:
        messages.info(request, "You're not authenticated. Please get in contact with an administrator.")
        if not request.user.is_anonymous():
            logger.warning("Unverified user " + request.user.username + " tried to place create a choice bet.")
            return redirect('profiles:profile')
        raise PermissionDenied


@login_required
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

        return render(request, 'bets/datebet_create_form.html', {'form': form})
    else:
        messages.info(request, "You're not authenticated. Please get in contact with an administrator.")
        if not request.user.is_anonymous():
            logger.warning("Unverified user " + request.user.username + " tried to place create a date bet.")
            return redirect('profiles:profile')
        raise PermissionDenied


class ModelFormWidgetMixin(object):
    def get_form_class(self):
        return modelform_factory(self.model, fields=self.fields, widgets=self.widgets)


class ChoiceBetUpdate(ModelFormWidgetMixin, UpdateView):
    model = ChoiceBet
    fields = ['name', 'description', 'end_bets_date', 'forbidden', 'end_date']
    template_name_suffix = '_update_form'
    widgets = {
        'end_bets_date': SelectDateWidget,
        # TODO fix django.db.utils.OperationalError: no such table: profiles_forbiddenuser
        # 'forbidden': SelectMultiple(attrs={'size': ForbiddenUser.objects.all().count()}),
        'end_date': SelectDateWidget
    }
    # TODO Form validation
    # TODO Edit choices
    # TODO Remove own user from forbidden?


class ChoiceBetDelete(DeleteView):
    model = ChoiceBet
    success_url = reverse_lazy('index')


class DateBetUpdate(ModelFormWidgetMixin, UpdateView):
    model = DateBet
    fields = ['name', 'description', 'end_bets_date', 'forbidden', 'time_period_start', 'time_period_end']
    template_name_suffix = '_update_form'
    widgets = {
        'end_bets_date': SelectDateWidget,
        # TODO fix django.db.utils.OperationalError: no such table: profiles_forbiddenuser
        # 'forbidden': SelectMultiple(attrs={'size': ForbiddenUser.objects.all().count()}),
        'time_period_start': SelectDateWidget,
        'time_period_end': SelectDateWidget
    }
    # TODO Form validation


class DateBetDelete(DeleteView):
    model = DateBet
    success_url = reverse_lazy('index')
