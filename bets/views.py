from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .forms import DateBetCreationForm


@login_required
def create_choice_bet(request):
    args = {}
    if request.method == 'POST':
        form = DateBetCreationForm(data=request.POST)
        if form.is_valid():
            form.save(request.user.profile)
    else:
        form = DateBetCreationForm()

    args['form'] = form

    return render(request, 'bets/create_date_bet.html', args)
