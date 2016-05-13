from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    # The user that this profile is associated with
    # Since each profile is associated with exactly one user, the user is the profiles primary key
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # Whether or not the users true identity has been verified
    verified = models.BooleanField(default=False)
    # The number of points the user has gained/lost
    points = models.IntegerField(default=0)
    # Has the user accepted the AGBs?
    accepted_agbs = models.BooleanField(default=False)

    def __str__(self):
        return self.user.__str__()


class ForbiddenUser(models.Model):
    # The name that will be shown to the user making the selection
    name = models.CharField(max_length=64)
    # Whether this person actually has an account
    has_account = models.BooleanField()
    # If the person has an account, it will be linked here.
    account = models.OneToOneField(Profile, blank=True, null=True)

    def __str__(self):
        return self.name
