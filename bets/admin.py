from django.contrib import admin

from .models import Bet, Choice, ChoiceBet, PlacedBet

admin.site.register(Bet)
admin.site.register(ChoiceBet)
admin.site.register(Choice)
admin.site.register(PlacedBet)
