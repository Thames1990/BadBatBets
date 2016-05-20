from django.contrib import admin
from .models import Profile, ForbiddenUser


class ProfileAdmin(admin.ModelAdmin):
    fields = ['user', 'account', 'verified', 'accepted_agb', 'accepted_privacy_policy']


admin.site.register(Profile, ProfileAdmin)
admin.site.register(ForbiddenUser)
