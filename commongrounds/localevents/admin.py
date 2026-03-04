from django.contrib import admin
from .models import Event, EventType


class EventInline(admin.TabularInline):
    model = Event


class EventTypeAdmin(admin.ModelAdmin):
    model = EventType
    search_fields = ['name',]
    list_display = ['name', 'description']
    inlines = [EventInline,]


class EventAdmin(admin.ModelAdmin):
    model = Event
    search_fields = ['title', 'description', 'location']
    list_filter = ['category', 'start_time', 'end_time']
    list_display = ['title', 'category', 'location',
                    'start_time', 'end_time', 'created_on',
                    'updated_on']


admin.site.register(EventType, EventTypeAdmin)
admin.site.register(Event, EventAdmin)
