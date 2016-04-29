from django.contrib import admin

from .models import BinaryBet, PlacedBinaryBet

admin.site.register(BinaryBet)
admin.site.register(PlacedBinaryBet)
