from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from .models import PlacedChoiceBet, PlacedDateBet, ChoiceBet, DateBet
from .forms import DateBetCreationForm
from .util import filter_visible_bets, user_can_bet_on_bet


def index_view(request):
    # TODO improve check
    if request.method == 'POST':
        request.user.profile.accepted_agb = True
        request.user.profile.save()

    if request.user.profile.accepted_agb:
        if request.user.is_authenticated():
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
        else:
            return render(request, 'profiles/login.html')
    else:
        return render(request, 'profiles/agb.html', {'accepted': True})


@login_required
def bet_view(request, prim_key):
    # TODO Exclude already bet on
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
                    'user_can_bet': user_can_bet_on_bet(request.user, date_bet)
                })
        else:
            return render(request, 'bets/bets.html', {
                'choice_bet': choice_bet,
                'user_can_bet': user_can_bet_on_bet(request.user, choice_bet)
            })
    else:
        return render(request, 'profiles/login.html')


@login_required
def bet_on_bet_view(request, prim_key):
    if request.user.is_authenticated():
        try:
            choice_bet = ChoiceBet.objects.get(prim_key=prim_key)
            choice = choice_bet.choice_set.get(description=request.POST['choice'])
        except ChoiceBet.DoesNotExist:
            try:
                date_bet = DateBet.objects.get(prim_key=prim_key)
            except DateBet.DoesNotExist:
                raise Http404(
                    "Neither a choice bet nor a date bet with id:" + str(prim_key) + " does exist."
                )
            else:
                placed_date_bet = PlacedDateBet(
                    placed_by=request.user.profile,
                    placed_on=date_bet,
                    placed_date=request.POST['date'],
                    placed=request.POST['placed'],
                )
                placed_date_bet.save()
                return HttpResponseRedirect(reverse('bets:index'))
        else:
            placed_choice_bet = PlacedChoiceBet(
                placed_by=request.user.profile,
                placed_on=choice_bet,
                chosen=choice,
                placed=request.POST['placed'],
            )
            placed_choice_bet.save()
            return HttpResponseRedirect(reverse('bets:index'))
    else:
        return render(request, 'profiles/login.html')


@login_required
def create_date_bet(request):
    args = {}
    if request.method == 'POST':
        form = DateBetCreationForm(data=request.POST)
        if form.is_valid():
            form.save(request.user.profile)
            # TODO redirect to bet page
    else:
        form = DateBetCreationForm()

    args['form'] = form

    return render(request, 'bets/create_date_bet.html', args)
