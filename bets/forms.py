from django.forms import ModelForm

from .models import DateBet


class DateBetCreationForm(ModelForm):
    class Meta:
        model = DateBet
        fields = ['name', 'description', 'pub_date', 'end_bets_date', 'time_period_start', 'time_period_end']
