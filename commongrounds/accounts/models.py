from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Profile(models.Model):
    ROLE_MEMBER = 'Member'
    ROLE_MARKET_SELLER = 'Market Seller'
    ROLE_EVENT_ORGANIZER = 'Event Organizer'
    ROLE_BOOK_CONTRIBUTOR = 'Book Contributor'
    ROLE_PROJECT_CREATOR = 'Project Creator'
    ROLE_COMMISSION_MAKER = 'Commission Maker'

    ROLE_CHOICES = [
        (ROLE_MEMBER, 'Member'),
        (ROLE_MARKET_SELLER, 'Market Seller'),
        (ROLE_EVENT_ORGANIZER, 'Event Organizer'),
        (ROLE_BOOK_CONTRIBUTOR, 'Book Contributor'),
        (ROLE_PROJECT_CREATOR, 'Project Creator'),
        (ROLE_COMMISSION_MAKER, 'Commission Maker'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=63)
    email_address = models.EmailField()
    role = models.CharField(
        max_length=32,
        choices=ROLE_CHOICES,
        default=ROLE_MEMBER,
    )

    def __str__(self):
        return self.display_name or self.user.username

    def get_absolute_url(self):
        return reverse('accounts:profile-update', args=[self.user.username])
