from django.db import models

from profiles.models import Profile


class Bet(models.Model):
    """Abstract superclass for fields which all bets have in common"""
    class Meta:
        abstract = True

    # Each bet has a user who owns it (usually the user that created it)
    owner = models.ForeignKey(Profile)
    # Name to be shown in the index
    name = models.CharField(max_length=64)
    # Detailed description of the bet
    description = models.TextField()
    # Date+Time when the bet was created
    created = models.DateTimeField(auto_now_add=True)
    # Date+Time when the bet is published
    pub_date = models.DateTimeField()

    def __str__(self):
        return self.name


class BinaryBet(Bet):
    """Bet which has a binary outcome"""

    # One of the two possible outcomes
    null_option = models.CharField(max_length=64)
    # The other possible outcome
    alternative_option = models.CharField(max_length=64)
