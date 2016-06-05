from django.utils import timezone
from django.db import models
from django.core.urlresolvers import reverse

from bets.util import key_gen
from profiles.models import Profile, ForbiddenUser
from ledger.models import Account


class Bet(models.Model):
    class Meta:
        abstract = True

    # Random key for each bet
    prim_key = models.PositiveIntegerField(primary_key=True, default=key_gen)
    # Each bet has a user who owns it (usually the user that created it)
    owner = models.ForeignKey(Profile)
    # Name to be shown in the index
    name = models.CharField(max_length=64)
    # Detailed description of the bet
    description = models.TextField()
    # Date+Time when the bet was created (timestamped automatically)
    created = models.DateTimeField(auto_now_add=True)
    # Date when the bet is published
    pub_date = models.DateField(auto_now_add=True)
    # After this, no further bets may be placed
    end_bets_date = models.DateField(blank=True, null=True)
    # Whether or not the bet has been resolved
    resolved = models.BooleanField(default=False)
    # People that are not allowed to see this bet
    forbidden = models.ManyToManyField(ForbiddenUser, blank=True)
    # Size of the pot
    pot = models.PositiveIntegerField(default=0)
    # Each bet also has an account
    account = models.OneToOneField(Account)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('bets:bet', kwargs={'prim_key': self.prim_key})

    def open_to_bets(self):
        if self.end_bets_date is None:
            return True
        else:
            return timezone.now().date() < self.end_bets_date


class PlacedBet(models.Model):
    class Meta:
        abstract = True

    # When the user made his bet
    created = models.DateTimeField(auto_now_add=True)
    # User that placed this bet
    placed_by = models.ForeignKey(Profile)
    # Amount the user placed
    placed = models.PositiveIntegerField()

    def __str__(self):
        return self.placed_on.name + ": " + self.placed_by.user.username


class ChoiceBet(Bet):
    # Date when the bet will be closed (if it is not resolved before)
    end_date = models.DateField(blank=True, null=True)
    # The choice that won in the end
    winning_choice = models.ForeignKey('Choice', null=True)


class Choice(models.Model):
    # The bet to which this choice belongs
    belongs_to = models.ForeignKey(ChoiceBet)
    # (Short) description of the choice
    description = models.CharField(max_length=64)
    # Number of people that have picked this choice
    picks = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.description


class PlacedChoiceBet(PlacedBet):
    # The bet it is placed on
    placed_on = models.ForeignKey(ChoiceBet)
    # Choice that the user selected
    chosen = models.ForeignKey(Choice)


class DateBet(Bet):
    # The date users bet on must be between start and end (if they exist)
    time_period_start = models.DateField(blank=True, null=True)
    time_period_end = models.DateField(blank=True, null=True)
    # The date which turned out to be correct
    winning_date = models.DateField(blank=True, null=True)


class PlacedDateBet(PlacedBet):
    # The bet it is placed on
    placed_on = models.ForeignKey(DateBet)
    # The date that the user bet on
    placed_date = models.DateField()
