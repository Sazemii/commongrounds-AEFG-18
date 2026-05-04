from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .models import Event, EventType, EventSignup


class LocalEventsListView(ListView):
    model = Event
    template_name = 'localevents/event_list.html'
    context_object_name = 'events'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            profile = user.profile
            context['organized_events'] = Event.objects.filter(
                organizer=profile)
            context['signed_up_events'] = Event.objects.filter(
                signups__user_registrant=profile
            )
            context['events'] = Event.objects.exclude(
                pk__in=context['organized_events'],
            ).exclude(
                pk__in=context['signed_up_events'],
            )
        return context


class LocalEventsDetailView(DetailView):
    model = Event
    template_name = 'localevents/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        user = self.request.user
        context['is_full'] = event.signups.count() >= event.event_capacity

        if user.is_authenticated:
            profile = user.profile
            context['is_organizer'] = profile in event.organizer.all()
        else:
            context['is_organizer'] = False

        return context
