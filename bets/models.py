from django.db import models
from django.utils import timezone

from bets.util import pkgen
from profiles.models import Profile, ForbiddenUser


class Bet(models.Model):
    BET_TYPES = (
        ('choice', 'Choices'),
    )

    prim_key = models.PositiveIntegerField(primary_key=True, default=pkgen)
    owner = models.ForeignKey(Profile)
    name = models.CharField(max_length=64)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    published_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    resolved = models.BooleanField(default=False)
    type = models.CharField(max_length=64, choices=BET_TYPES)
    forbidden = models.ManyToManyField(ForbiddenUser)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name


class Choice(models.Model):
    belongs_to = models.ForeignKey(Bet)
    description = models.CharField(max_length=64)

    def __str__(self):
        return self.belongs_to.name + ": " + self.description


class ChoiceBet(models.Model):
    placed_by = models.ForeignKey(Profile)
    placed_on = models.ForeignKey(Bet)
    chosen = models.ForeignKey(Choice)
    placed = models.PositiveIntegerField()

    def __str__(self):
        return self.placed_on.name + ": " + self.placed_by.user.username
