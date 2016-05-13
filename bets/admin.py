from django.contrib import admin

from .models import ChoiceBet, Choice, PlacedChoiceBet, DateBet, PlacedDateBet


class ChoiceInLine(admin.TabularInline):
    model = Choice
    extra = 2


class ChoiceBetAdmin(admin.ModelAdmin):
    fieldsets = [
        ('General', {'fields': ['name', 'description']}),
        ('People', {'fields': ['owner', 'forbidden']}),
        ('Dates', {'fields': ['pub_date', 'end_bets_date', 'end_date']}),
        ('Misc', {
            'fields': ['resolved'],
            'classes': ('collapse',),
        },),
    ]
    inlines = [ChoiceInLine]
    list_display = ('name', 'created', 'pub_date', 'end_date', 'resolved')


class DateBetAdmin(admin.ModelAdmin):
    fieldsets = [
        ('General', {'fields': ['name', 'description']}),
        ('People', {'fields': ['owner', 'forbidden']}),
        ('Dates', {'fields': ['pub_date', 'end_bets_date']}),
        ('Misc', {
            'fields': ['resolved'],
            'classes': ('collapse',),
        },),
    ]
    list_display = ('name', 'created', 'pub_date', 'resolved')

admin.site.register(ChoiceBet, ChoiceBetAdmin)
admin.site.register(PlacedChoiceBet)
admin.site.register(DateBet, DateBetAdmin)
admin.site.register(PlacedDateBet)
