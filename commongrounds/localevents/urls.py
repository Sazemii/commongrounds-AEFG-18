from django.urls import path
from .views import LocalEventsListView, LocalEventsDetailView

urlpatterns = [
    path('events',
         LocalEventsListView.as_view(),
         name='event_list'),
    path('event/<int:pk>',
         LocalEventsDetailView.as_view(),
         name='event_detail')
]

app_name = 'localevents'
