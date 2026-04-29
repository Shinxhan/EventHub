from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from events.models import Event, Registration
from users.models import User
import datetime


@login_required
def dashboard(request):
    if request.user.is_admin():
        return _admin_dashboard(request)
    elif request.user.is_organizer():
        return _organizer_dashboard(request)
    else:
        return _student_dashboard(request)


def _admin_dashboard(request):
    total_users = User.objects.count()
    total_events = Event.objects.count()
    total_registrations = Registration.objects.count()

    recent_events = Event.objects.all()[:5]
    recent_registrations = Registration.objects.select_related('user', 'event')[:10]

    context = {
        'total_users': total_users,
        'total_events': total_events,
        'total_registrations': total_registrations,
        'recent_events': recent_events,
        'recent_registrations': recent_registrations,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


def _organizer_dashboard(request):
    my_events = Event.objects.filter(organizer=request.user)
    total_events = my_events.count()
    total_participants = my_events.aggregate(
        total=Count('registrations')
    )['total'] or 0

    upcoming_events = my_events.filter(
        date__gte=timezone.now().date()
    ).order_by('date', 'time')

    events_with_counts = my_events.annotate(
        participant_count=Count('registrations')
    ).order_by('-date', '-time')[:5]

    context = {
        'total_events': total_events,
        'total_participants': total_participants,
        'upcoming_events': upcoming_events,
        'events_with_counts': events_with_counts,
    }
    return render(request, 'dashboard/organizer_dashboard.html', context)


def _student_dashboard(request):
    registered_events = Event.objects.filter(
        registrations__user=request.user
    ).order_by('-date', '-time')

    upcoming_events = Event.objects.filter(
        date__gte=timezone.now().date()
    ).exclude(
        registrations__user=request.user
    ).order_by('date', 'time')[:5]

    all_events = Event.objects.filter(
        date__gte=timezone.now().date()
    ).order_by('date', 'time')[:10]

    context = {
        'registered_events': registered_events,
        'upcoming_events': upcoming_events,
        'all_events': all_events,
    }
    return render(request, 'dashboard/student_dashboard.html', context)
