from django.contrib import admin

from .models import Bet, Choice, ChoiceBet

admin.site.register(Bet)
admin.site.register(Choice)
admin.site.register(ChoiceBet)
