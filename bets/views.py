from django.http import HttpResponse
from django.template import loader
from .models import BinaryBet


def index(request):
    all_binary_bets = BinaryBet.objects.all()
    template = loader.get_template('bets/index.html')
    context = {
        'all_binary_bets': all_binary_bets
    }
    return HttpResponse(template.render(context, request))


def bets(request, prim_key):
    return HttpResponse("<h2>Bet " + str(prim_key) + "</h2>")
