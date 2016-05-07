from django.core.urlresolvers import reverse
from django.db import models

from bets.util import pkgen
from profiles.models import Profile, ForbiddenUser


class Bet(models.Model):
    BET_TYPES = (
        ('choice', 'Choices'),
    )

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
    # Date when the bet will be closed (if it is not resolved before)
    end_date = models.DateField(blank=True, null=True)
    # Whether or not the bet has been resolved
    resolved = models.BooleanField(default=False)
    # Type of the bet
    type = models.CharField(max_length=64, choices=BET_TYPES)
    # People that are not allowed to see this bet
    forbidden = models.ManyToManyField(ForbiddenUser)

    def get_absolute_url(self):
        return reverse('bets:bet', kwargs={'prim_key': self.prim_key})

    def __str__(self):
        return self.name


class Choice(models.Model):
    # The bet to which this choice belongs
    belongs_to = models.ForeignKey(Bet)
    # (Short) description of the choice
    description = models.CharField(max_length=64)

    def __str__(self):
        return self.belongs_to.name + ": " + self.description


class ChoiceBet(models.Model):
    # User that placed this bet
    placed_by = models.ForeignKey(Profile)
    # The bet it is placed on
    placed_on = models.ForeignKey(Bet)
    # Choice that the user selected
    chosen = models.ForeignKey(Choice)
    # Amount the user placed
    placed = models.PositiveIntegerField()

    def __str__(self):
        return self.placed_on.name + ": " + self.placed_by.user.username
