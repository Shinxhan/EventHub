from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events'
    )
    max_participants = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-time']

    def __str__(self):
        return self.title

    def is_upcoming(self):
        event_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        return event_datetime > timezone.now()

    def participant_count(self):
        return self.registrations.count()

    def is_full(self):
        return self.registrations.count() >= self.max_participants


class Registration(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} registered for {self.event.title}"

    def clean(self):
        # Prevent duplicate registrations
        if Registration.objects.filter(user=self.user, event=self.event).exists():
            raise ValidationError('You have already registered for this event.')
        # Respect max participant limit
        if self.event.is_full():
            raise ValidationError('This event is full.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
