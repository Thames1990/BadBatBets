from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import ChoiceBet, DateBet
from .util import create_choices
from ledger.models import Account

from profiles.models import ForbiddenUser


class ChoiceBetCreationForm(forms.ModelForm):
    class Meta:
        model = ChoiceBet
        fields = ['name', 'description', 'pub_date', 'end_bets_date', 'end_date']

    pub_date = forms.DateField(widget=forms.SelectDateWidget, required=False)
    end_bets_date = forms.DateField(widget=forms.SelectDateWidget, required=False)
    end_date = forms.DateField(widget=forms.SelectDateWidget, required=False)
    forbidden = forms.ModelMultipleChoiceField(queryset=ForbiddenUser.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super(ChoiceBetCreationForm, self).__init__(*args, **kwargs)
        self.fields['forbidden'].widget.attrs["size"] = ForbiddenUser.objects.all().count()

    def clean_pub_date(self):
        pub_date = self.cleaned_data.get('pub_date')

        if pub_date is None:
            return pub_date

        if pub_date <= timezone.now().date():
            raise ValidationError(
                'If you set a publication date, it has to be in the future. If you want the bet to be visible '
                'immediately, do not set a publication date.',
                code='pub_date_not_in_future')

        return pub_date

    def clean_end_bets_date(self):
        pub_date = self.cleaned_data.get('pub_date')
        end_bets_date = self.cleaned_data.get('end_bets_date')

        if end_bets_date is None:
            return end_bets_date

        if pub_date is None:
            if end_bets_date <= timezone.now().date():
                raise ValidationError('Must give at least 1 day to place bets.', code='end_bets_not_in_future')
        elif end_bets_date <= pub_date:
            raise ValidationError('Bet placement has to be open after publish date.',
                                  code='end_bets_date_before_pub_date')

        return end_bets_date

    def clean_end_date(self):
        pub_date = self.cleaned_data.get('pub_date')
        end_bets_date = self.cleaned_data.get('end_bets_date')
        end_date = self.cleaned_data.get('end_date')

        if end_date is None:
            return end_date

        if end_date < end_bets_date:
            raise ValidationError('Placement of bets cannot be sustained after the bet is closed',
                                  code='end_date_before_end_bets_date')

        if end_date <= pub_date:
            raise ValidationError('The timespan between the publishement date and end date must be at least one day.',
                                  code='bet_timespan_too_short')

        return end_date

    def save(self, request):
        name = self.cleaned_data['name']
        description = self.cleaned_data['description']
        pub_date = self.cleaned_data['pub_date']
        end_bets_date = self.cleaned_data['end_bets_date']
        end_date = self.cleaned_data.get('end_date')
        forbidden = self.cleaned_data['forbidden']

        account = Account(name=name, type='b')
        account.save()

        new_bet = ChoiceBet(
            owner=request.user.profile,
            name=name,
            description=description,
            end_bets_date=end_bets_date,
            end_date=end_date,
            account=account
        )
        try:
            choices = create_choices(request, new_bet)
        except ValidationError:
            raise

        new_bet.save()
        for choice in choices:
            choice.save()

        for forbidden_user in forbidden:
            new_bet.forbidden.add(forbidden_user)

        if pub_date is not None:
            new_bet.pub_date = pub_date
            new_bet.save()

        return new_bet


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
                'If you set a publication date, it has to be in the future. If you want the bet to be visible '
                'immediately, do not set a publication date.',
                code='pub_date_not_in_future')

        return pub_date

    def clean_end_bets_date(self):
        pub_date = self.cleaned_data.get('pub_date')
        end_bets_date = self.cleaned_data.get('end_bets_date')

        if end_bets_date is None:
            return end_bets_date

        if pub_date is None:
            if end_bets_date <= timezone.now().date():
                raise ValidationError('Must give at least 1 day to place bets.', code='end_bets_not_in_future')
        elif end_bets_date < pub_date:
            raise ValidationError('Bet placement has to be open after publish date.',
                                  code='end_bets_date_before_pub_date')

        return end_bets_date

    def clean_time_period_start(self):
        pub_date = self.cleaned_data.get('pub_date')
        time_period_start = self.cleaned_data.get('time_period_start')

        if time_period_start is None:
            return time_period_start

        if pub_date is None:
            if time_period_start <= timezone.now().date():
                raise ValidationError(
                    'The period to bet on must be in the future.', code='time_period_start_not_in_future')
        elif time_period_start <= pub_date:
            raise ValidationError(
                'The period to bet on has to start after Publication. Do not set a start date if you want the '
                'period to start at publication.',
                code='time_period_start_not_greater_pub')

        return time_period_start

    def clean_time_period_end(self):
        pub_date = self.cleaned_data.get('pub_date')
        time_period_start = self.cleaned_data.get('time_period_start')
        time_period_end = self.cleaned_data.get('time_period_end')

        if time_period_end is None:
            return time_period_end

        if (pub_date is None) and (time_period_start is None):
            if time_period_end <= timezone.now().date():
                raise ValidationError('The period to bet on must not end in the past', code='period_end_not_in_future')
        elif not (time_period_start is None):
            if time_period_start >= time_period_end:
                raise ValidationError('The period to bet on must end after it has started',
                                      code='period_end_not_greater_period_start')
        elif not (pub_date is None):
            if time_period_end <= pub_date:
                raise ValidationError('The period to bet on must not end before the bet is visible',
                                      code='period_end_not_greater_pub')

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

        new_bet = DateBet.objects.create(
            owner=user,
            name=name,
            description=description,
            end_bets_date=end_bets_date,
            time_period_start=time_period_start,
            time_period_end=time_period_end,
            account=account
        )

        for forbidden_user in forbidden:
            new_bet.forbidden.add(forbidden_user)

        if pub_date is not None:
            new_bet.pub_date = pub_date
            new_bet.save()

        return new_bet
