from django.db import models
from django.urls import reverse


class EventType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        EventType,
        on_delete=models.SET_NULL,
        null=True,
        related_name="events")
    organizer = models.ManyToManyField(
        'accounts.Profile',
        related_name='organized_events',)
    event_image = models.ImageField(upload_to='images/')
    description = models.TextField()
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    event_capacity = models.PositiveIntegerField()
    status = models.CharField(
        max_length=67,
        choices=[
            ('Available', 'Available'),
            ('Full', 'Full'),
            ('Done', 'Done'),
            ('Cancelled', 'Cancelled'),
        ],
        default='Available'
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_on']

    def get_absolute_url(self):
        return reverse('localevents:event_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title


class EventSignup(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='signups',
        null=True,
        blank=True,)
    user_registrant = models.ForeignKey(
        'accounts.Profile',
        on_delete=models.CASCADE,
        related_name='event_signups',
        null=True,
        blank=True,)
    new_registrant = models.CharField(
        max_length=255,
        blank=True,)

    def __str__(self):
        if self.user_registrant:
            return f"{self.user_registrant} signed up for {self.event}"
        else:
            return f"{self.new_registrant} signed up for {self.event}"
