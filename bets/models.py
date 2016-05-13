from django.db import models
from django.utils import timezone

from bets.util import pkgen
from profiles.models import Profile, ForbiddenUser


class Bet(models.Model):
    prim_key = models.PositiveIntegerField(primary_key=True, default=pkgen)
    owner = models.ForeignKey(Profile)
    name = models.CharField(max_length=64)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    published_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    forbidden_users = models.ManyToManyField(ForbiddenUser)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name


class Choice(models.Model):
    description = models.CharField(max_length=64)

    def __str__(self):
        return self.description


class ChoiceBet(Bet):
    choices = models.ManyToManyField(Choice)


class PlacedBet(models.Model):
    placed_by = models.ForeignKey(Profile)
    placed_on = models.ForeignKey(Bet)
    chosen = models.ForeignKey(Choice)
    placed = models.PositiveIntegerField()

    def __str__(self):
        return self.placed_on.name + ": " + self.placed_by.user.username
