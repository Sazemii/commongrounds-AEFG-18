from django.urls import path
# , LocalEventsCreateView, LocalEventsUpdateView, LocalEventsSignupView
from .views import LocalEventsListView, LocalEventsDetailView

urlpatterns = [
    path('events',
         LocalEventsListView.as_view(),
         name='event_list'),
    path('event/<int:pk>',
         LocalEventsDetailView.as_view(),
         name='event_detail'),
    #     path('event/add',
    #          LocalEventsCreateView.as_view(),
    #          name='event_add'),
    #     path('event/<int:pk>/edit',
    #          LocalEventsUpdateView.as_view(),
    #          name='event_edit'),
    #     path('event/<int:pk>/signup',
    #          LocalEventsSignupView.as_view(),
    #          name='event_signup'),
]

app_name = 'localevents'
