from django.contrib import admin
from .models import Event, EventType, EventSignup


class EventInline(admin.TabularInline):
    model = Event
    extra = 0


class EventSignupInline(admin.TabularInline):
    model = EventSignup
    extra = 0


class EventTypeAdmin(admin.ModelAdmin):
    model = EventType
    search_fields = ['name',]
    list_display = ['name', 'description']
    inlines = [EventInline,]


class EventAdmin(admin.ModelAdmin):
    model = Event
    search_fields = ['title', 'description', 'location']
    list_filter = ['category', 'start_time', 'end_time', 'organizer', 'status']
    list_display = ['title', 'category', 'location',
                    'start_time', 'end_time', 'created_on',
                    'updated_on']
    inlines = [EventSignupInline,]


admin.site.register(EventType, EventTypeAdmin)
admin.site.register(Event, EventAdmin)
