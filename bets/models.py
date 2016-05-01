from django.db import models

from bets.util import pkgen
from profiles.models import Profile


class Bet(models.Model):
    """Abstract superclass for fields which all bets have in common"""
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
    # Date+Time when the bet is published
    pub_date = models.DateTimeField()
    # Whether or not the bet has been resolved
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class BinaryBet(Bet):
    """Bet which has a binary outcome"""

    # One of the two possible outcomes
    null_option = models.CharField(max_length=64)
    # The other possible outcome
    alternative_option = models.CharField(max_length=64)


class PlacedBinaryBet(models.Model):
    """A bet placed by someone on a binary bet"""

    # Random key for each bet
    prim_key = models.PositiveIntegerField(primary_key=True, default=pkgen)
    # The bet it was placed on
    placed_on = models.ForeignKey(BinaryBet)
    # The user who placed the bet
    placed_by = models.ForeignKey(Profile)
    # Amount of x placed
    placed_amount = models.PositiveIntegerField()
    # Whether the user chose the alternative and not the null option
    chose_alternative = models.BooleanField()
    # Timestamp of when the bet was placed
    placed_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.placed_on.__str__() + ": " + self.placed_by.__str__()
