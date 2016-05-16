from django import forms

from .models import DateBet
from profiles.models import ForbiddenUser


class DateBetCreationForm(forms.ModelForm):

    class Meta:
        model = DateBet
        fields = ['name', 'description', 'pub_date', 'end_bets_date', 'time_period_start', 'time_period_end']

    pub_date = forms.DateField(widget=forms.SelectDateWidget)
    end_bets_date = forms.DateField(widget=forms.SelectDateWidget)
    time_period_start = forms.DateField(widget=forms.SelectDateWidget, required=False)
    time_period_end = forms.DateField(widget=forms.SelectDateWidget, required=False)
    forbidden = forms.ModelMultipleChoiceField(queryset=ForbiddenUser.objects.all())

    def save(self, user):
        name = self.cleaned_data['name']
        description = self.cleaned_data['description']
        pub_date = self.cleaned_data['pub_date']
        end_bets_date = self.cleaned_data['end_bets_date']
        time_period_start = self.cleaned_data['time_period_start']
        time_period_end = self.cleaned_data['time_period_end']
        forbidden = self.cleaned_data['forbidden']

        print(forbidden)

        new_bet = DateBet(
            owner=user,
            name=name,
            description=description,
            pub_date=pub_date,
            end_bets_date=end_bets_date,
            time_period_start=time_period_start,
            time_period_end=time_period_end,
        )
        new_bet.save()

        for forbidden_user in forbidden:
            new_bet.forbidden.add(forbidden_user)

