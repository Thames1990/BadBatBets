from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse, reverse_lazy
from django.views import generic
from django.views.generic import CreateView, UpdateView, DeleteView

from .models import Bet, ChoiceBet, Choice


def index_view(request):
    if request.user.is_authenticated():
        all_bets = Bet.objects.all()
        all_choice_bets = ChoiceBet.objects.all()
        context = {
            'all_bets': all_bets,
            'all_choice_bets': all_choice_bets
        }
        return render(request, 'bets/index.html', context)
    else:
        return render(request, 'profiles/login.html')


def bet_view(request, prim_key):
    # TODO filter for forbidden users
    if request.user.is_authenticated():
        try:
            bet = Bet.objects.get(prim_key=prim_key)
        except Bet.DoesNotExist:
            try:
                choice_bet = ChoiceBet.objects.get(prim_key=prim_key)
            except ChoiceBet.DoesNotExist:
                raise Http404("Neither a binary bet nor a placed binary bet with id:" + str(prim_key) + " does exist.")
            return render(request, 'bets/bets.html', {'choice_bet': choice_bet})
        return render(request, 'bets/bets.html', {'bet': bet})
    else:
        return render(request, 'profiles/login.html')


def choice_bet_view(request, prim_key):
    if request.user.is_authenticated():
        bet = get_object_or_404(Bet, prim_key=prim_key)
        choice_bet = ChoiceBet(
            placed_by=request.user.profile,
            placed_on=bet,
            chosen=get_object_or_404(Choice, belongs_to=bet, description=request.POST['choice']),
            placed=request.POST['placed'],
        )
        choice_bet.save()
        return HttpResponseRedirect(reverse('bets:index'))
    else:
        return render(request, 'profiles/login.html')


class IndexView(generic.ListView):
    template_name = 'bets/index.html'

    def get_queryset(self):
        return Bet.objects.all()

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context.update({
            'bets': Bet.objects.all(),
            'choice_bets': ChoiceBet.objects.all()
        })
        return context


class BetView(generic.DetailView):
    model = Bet
    template_name = 'bets/bets.html'


class BetCreate(CreateView):
    model = Bet
    fields = [
        'owner',
        'name',
        'description',
        'pub_date',
        'end_date',
        'type',
        'forbidden'
    ]


class BetUpdate(UpdateView):
    model = Bet
    success_url = reverse_lazy('bets:index')
    fields = [
        'owner',
        'name',
        'description',
        'pub_date',
        'end_date',
        'type',
        'forbidden'
    ]


class BetDelete(DeleteView):
    model = Bet
    success_url = reverse_lazy('bets:index')
