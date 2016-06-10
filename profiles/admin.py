from django.contrib import admin
from .models import Profile, ForbiddenUser, Feedback


class ProfileAdmin(admin.ModelAdmin):
    fields = ['user', 'account', 'verified', 'accepted_general_terms_and_conditions', 'accepted_privacy_policy']
    list_display = ['user', 'verified']


class ForbiddenUserAdmin(admin.ModelAdmin):
    list_display = ['name', 'has_account']


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['provided_by', 'feedback', 'resolved']


admin.site.register(Profile, ProfileAdmin)
admin.site.register(ForbiddenUser, ForbiddenUserAdmin)
admin.site.register(Feedback, FeedbackAdmin)
