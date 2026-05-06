from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'category', 'event_image',
                  'description', 'location', 'start_time',
                  'end_time', 'event_capacity', 'status',
                  ]
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}),
        }
