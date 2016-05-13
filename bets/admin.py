from django.contrib import admin

from .models import ChoiceBet, Choice, PlacedChoiceBet


class ChoiceInLine(admin.TabularInline):
    model = Choice
    extra = 2


class ChoiceBetAdmin(admin.ModelAdmin):
    fieldsets = [
        ('General', {'fields': ['name', 'description']}),
        ('People', {'fields': ['owner', 'forbidden']}),
        ('Dates', {'fields': ['pub_date', 'end_bets', 'end_date']}),
        ('Misc', {
            'fields': ['resolved'],
            'classes': ('collapse',),
        },),
    ]
    inlines = [ChoiceInLine]
    list_display = ('name', 'created', 'pub_date', 'end_date', 'resolved')

admin.site.register(ChoiceBet, ChoiceBetAdmin)
