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

    def __str__(self):
        return self.user.__str__()
