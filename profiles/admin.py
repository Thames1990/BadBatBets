from django.contrib import admin
from .models import Profile, ForbiddenUser

admin.site.register(Profile)
admin.site.register(ForbiddenUser)
