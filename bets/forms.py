from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from .models import DateBet
from ledger.models import Account

from profiles.models import ForbiddenUser


class DateBetCreationForm(forms.ModelForm):
    class Meta:
        model = DateBet
        fields = ['name', 'description', 'pub_date', 'end_bets_date', 'time_period_start', 'time_period_end']

    pub_date = forms.DateField(widget=forms.SelectDateWidget, required=False)
    end_bets_date = forms.DateField(widget=forms.SelectDateWidget, required=False)
    time_period_start = forms.DateField(widget=forms.SelectDateWidget, required=False)
    time_period_end = forms.DateField(widget=forms.SelectDateWidget, required=False)
    forbidden = forms.ModelMultipleChoiceField(queryset=ForbiddenUser.objects.all(), required=False)

    def clean_pub_date(self):
        pub_date = self.cleaned_data.get('pub_date')

        if pub_date is None:
            return pub_date

        if pub_date <= timezone.now().date():
            raise ValidationError(
                _('If you set a publication date, it has to be in the future. '
                  'If you want the bet to be visible immediately, do not set a publication date.'),
                code='pub_date_not_in_future',
            )

        return pub_date

    def clean_end_bets_date(self):
        pub_date = self.cleaned_data.get('pub_date')
        end_bets_date = self.cleaned_data.get('end_bets_date')

        if end_bets_date is None:
            return end_bets_date

        if pub_date is None:
            if end_bets_date <= timezone.now().date():
                raise ValidationError(
                    _('Must give at least 1 day to place bets.'),
                    code='end_bets_not_greater_pub',
                )
        elif end_bets_date < pub_date:
            raise ValidationError(
                _('Must give at least 1 day to place bets.'),
                code='end_bets_not_in_future',
            )

        return end_bets_date

    def clean_time_period_start(self):
        pub_date = self.cleaned_data.get('pub_date')
        time_period_start = self.cleaned_data.get('time_period_start')

        if time_period_start is None:
            return time_period_start

        if pub_date is None:
            if time_period_start <= timezone.now().date():
                raise ValidationError(
                    _('The period to bet on must start after Publication.'
                      'Do not set a start date if you want the period to start immediately'),
                    code='period_start_not_in_future',
                )
        elif time_period_start <= pub_date:
            raise ValidationError(
                _('The period to bet on must start after Publication.'
                  'Do not set a start date if you want the period to start at publication'),
                code='period_start_not_greater_pub',
            )

        return time_period_start

    def clean_time_period_end(self):
        pub_date = self.cleaned_data.get('pub_date')
        time_period_start = self.cleaned_data.get('time_period_start')
        time_period_end = self.cleaned_data.get('time_period_end')

        if time_period_end is None:
            return time_period_end

        if (pub_date is None) and (time_period_start is None):
            if time_period_end <= timezone.now().date():
                raise ValidationError(
                    _('The period to bet on must not end in the past'),
                    code='period_end_not_in_future',
                )
        elif not (time_period_start is None):
            if time_period_start >= time_period_end:
                raise ValidationError(
                    _('The period to bet on must end after it has started'),
                    code='period_end_not_greater_period_start',
                )
        elif not (pub_date is None):
            if time_period_end <= pub_date:
                raise ValidationError(
                    _('The period to bet on must not end before the bet is visible'),
                    code='period_end_not_greater_pub',
                )

        return time_period_end

    def save(self, user):
        name = self.cleaned_data['name']
        description = self.cleaned_data['description']
        pub_date = self.cleaned_data['pub_date']
        end_bets_date = self.cleaned_data['end_bets_date']
        time_period_start = self.cleaned_data['time_period_start']
        time_period_end = self.cleaned_data['time_period_end']
        forbidden = self.cleaned_data['forbidden']

        account = Account(name=name, type='b')
        account.save()

        new_bet = DateBet(
            owner=user,
            name=name,
            description=description,
            pub_date=pub_date,
            end_bets_date=end_bets_date,
            time_period_start=time_period_start,
            time_period_end=time_period_end,
            account=account
        )
        new_bet.save()

        for forbidden_user in forbidden:
            new_bet.forbidden.add(forbidden_user)

        return new_bet.prim_key
