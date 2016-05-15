from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .forms import DateBetCreationForm


@login_required
def create_choice_bet(request):
    args = {}
    if request.method == 'POST':
        form = DateBetCreationForm(data=request)
        # TODO: Do stuff with it - (we first need a way to represent the forbidden users though...)
    else:
        form = DateBetCreationForm()

    args['form'] = form

    return render(request, 'bets/create_date_bet.html', args)
