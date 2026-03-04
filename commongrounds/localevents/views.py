from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .models import Event, EventType


class LocalEventsListView(ListView):
    model = Event
    template_name = 'localevents/event_list.html'
    context_object_name = 'events'
    pass


class LocalEventsDetailView(DetailView):
    model = Event
    template_name = 'localevents/event_detail.html'
    context_object_name = 'event'
    pass
