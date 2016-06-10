from django.contrib import admin

from .models import ChoiceBet, Choice, PlacedChoiceBet, DateBet, PlacedDateBet


class ChoiceInLine(admin.TabularInline):
    model = Choice
    extra = 2


class ChoiceBetAdmin(admin.ModelAdmin):
    fieldsets = [
        ('General', {'fields': ['name', 'description', 'account']}),
        ('People', {'fields': ['owner', 'forbidden']}),
        ('Dates', {'fields': ['end_bets_date', 'end_date']}),
        ('Misc', {
            'fields': ['resolved'],
            'classes': ('collapse',),
        },),
    ]
    inlines = [ChoiceInLine]
    list_display = ('name', 'created', 'pub_date', 'end_date', 'resolved')


class PlacedChoiceBetAdmin(admin.ModelAdmin):
    list_display = ('placed_by', 'placed_on', 'chosen', 'placed')


class DateBetAdmin(admin.ModelAdmin):
    fieldsets = [
        ('General', {'fields': ['name', 'description']}),
        ('People', {'fields': ['owner', 'forbidden']}),
        ('Dates', {'fields': ['end_bets_date']}),
        ('Time Period', {
            'fields': ['time_period_start', 'time_period_end'],
            'classes': ('collapse',)
        }),
        ('Misc', {
            'fields': ['resolved'],
            'classes': ('collapse',),
        },),
    ]
    list_display = ('name', 'created', 'pub_date', 'resolved')


class PlacedDateBetAdmin(admin.ModelAdmin):
    list_display = ('placed_by', 'placed_on', 'placed_date', 'placed')


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('belongs_to', 'description', 'picks')


admin.site.register(ChoiceBet, ChoiceBetAdmin)
admin.site.register(PlacedChoiceBet, PlacedChoiceBetAdmin)
admin.site.register(DateBet, DateBetAdmin)
admin.site.register(PlacedDateBet, PlacedDateBetAdmin)
admin.site.register(Choice, ChoiceAdmin)
