from django.db import models


class Entry(models.Model):
    """Entry in the journal"""

    # Name of the kind of event that occured
    name = models.CharField(max_length=64)
    # In-depth description of what happened
    content = models.TextField()
    # Who/What noticed the problem
    raised_by = models.CharField(max_length=64)
    # Whether or not the problem has been resolved
    resolved = models.BooleanField(default=False)
    # What did you do to resolve the problem
    resolve_comment = models.TextField(default="")
