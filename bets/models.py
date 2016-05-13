from django.utils import timezone
from django.db import models

from bets.util import pkgen
from profiles.models import Profile, ForbiddenUser


class Bet(models.Model):

    class Meta:
        abstract = True

    # Random key for each bet
    prim_key = models.PositiveIntegerField(primary_key=True, default=pkgen)
    # Each bet has a user who owns it (usually the user that created it)
    owner = models.ForeignKey(Profile)
    # Name to be shown in the index
    name = models.CharField(max_length=64)
    # Detailed description of the bet
    description = models.TextField()
    # Date+Time when the bet was created (timestamped automatically)
    created = models.DateTimeField(auto_now_add=True)
    # Date when the bet is published
    pub_date = models.DateField()
    # After this, no further bets may be placed
    end_bets_date = models.DateField(blank=True, null=True)
    # Whether or not the bet has been resolved
    resolved = models.BooleanField(default=False)
    # People that are not allowed to see this bet
    forbidden = models.ManyToManyField(ForbiddenUser)

    def open_to_bets(self):
        if self.end_bets is None:
            return True
        else:
            return timezone.now() < self.end_bets


class PlacedBet(models.Model):

    class Meta:
        abstract = True

    # User that placed this bet
    placed_by = models.ForeignKey(Profile)
    # Amount the user placed
    placed = models.PositiveIntegerField()

    def __str__(self):
        return self.placed_on.name + ": " + self.placed_by.user.username


class ChoiceBet(Bet):
    # Date when the bet will be closed (if it is not resolved before)
    end_date = models.DateField(blank=True, null=True)


class Choice(models.Model):
    # The bet to which this choice belongs
    belongs_to = models.ForeignKey(ChoiceBet)
    # (Short) description of the choice
    description = models.CharField(max_length=64)

    # TODO: This does not wok - and i have no idea, why!
    # def __str__(self):
    #    return self.belongs_to.name + ": " + self.description


class PlacedChoiceBet(PlacedBet):
    # The bet it is placed on
    placed_on = models.ForeignKey(ChoiceBet)
    # Choice that the user selected
    chosen = models.ForeignKey(Choice)


class DateBet(Bet):
    # If don't know of any additional fields yet - but you can't have an empty Model
    foobar = models.CharField(max_length=6, default='foobar')


class PlacedDateBet(PlacedBet):
    # The bet it is placed on
    placed_on = models.ForeignKey(DateBet)
    # The date that the user bet on
    placed_date = models.DateField()
