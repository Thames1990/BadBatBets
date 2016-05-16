from django.contrib import admin

from .models import Entry


class EntryAdmin(admin.ModelAdmin):
    list_display = ['name', 'resolved']

admin.site.register(Entry, EntryAdmin)
