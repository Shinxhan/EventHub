from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Event, Registration
from .forms import EventForm


@login_required
def event_register(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if event.registrations.filter(user=request.user).exists():
        messages.info(request, 'You are already registered for this event.')
        return redirect('event_detail', pk=pk)

    if event.is_full():
        messages.error(request, 'This event is full.')
        return redirect('event_detail', pk=pk)

    if not event.is_upcoming():
        messages.error(request, 'You cannot register for a past event.')
        return redirect('event_detail', pk=pk)

    Registration.objects.create(user=request.user, event=event)
    messages.success(request, f'Successfully registered for "{event.title}"!')
    return redirect('event_detail', pk=pk)


@login_required
def event_unregister(request, pk):
    event = get_object_or_404(Event, pk=pk)
    registration = event.registrations.filter(user=request.user).first()

    if registration:
        registration.delete()
        messages.success(request, f'Successfully unregistered from "{event.title}".')
    else:
        messages.info(request, 'You are not registered for this event.')

    return redirect('event_detail', pk=pk)


def event_list(request):
    events = Event.objects.all().select_related('organizer')
    query = request.GET.get('q')
    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        )
    return render(request, 'events/event_list.html', {'events': events})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    registrations = event.registrations.select_related('user').all()
    is_registered = False
    if request.user.is_authenticated:
        is_registered = event.registrations.filter(user=request.user).exists()
    return render(request, 'events/event_detail.html', {
        'event': event,
        'registrations': registrations,
        'is_registered': is_registered,
    })


@login_required
def event_create(request):
    if not request.user.is_organizer() and not request.user.is_admin():
        messages.error(request, 'You do not have permission to create events.')
        return redirect('event_list')

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm()

    return render(request, 'events/event_form.html', {'form': form, 'title': 'Create Event'})


@login_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.user != event.organizer and not request.user.is_admin():
        messages.error(request, 'You do not have permission to edit this event.')
        return redirect('event_detail', pk=pk)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)

    return render(request, 'events/event_form.html', {'form': form, 'title': 'Edit Event', 'event': event})


@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.user != event.organizer and not request.user.is_admin():
        messages.error(request, 'You do not have permission to delete this event.')
        return redirect('event_detail', pk=pk)

    if request.method == 'POST':
        event_title = event.title
        event.delete()
        messages.success(request, f'Event "{event_title}" deleted successfully!')
        return redirect('event_list')

    return render(request, 'events/event_confirm_delete.html', {'event': event})
