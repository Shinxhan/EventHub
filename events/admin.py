from django.contrib import admin
from .models import Event, Registration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'location', 'organizer', 'max_participants', 'participant_count')
    list_filter = ('date', 'location')
    search_fields = ('title', 'description')
    date_hierarchy = 'date'


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'timestamp')
    list_filter = ('event',)
    search_fields = ('user__username', 'event__title')
