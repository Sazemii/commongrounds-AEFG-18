from datetime import timedelta

from django.db import models
from django.urls import reverse

from accounts.models import Profile


class Genre(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        null=True,
    )
    contributor = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contributed_books',
    )
    author = models.CharField(max_length=255)
    synopsis = models.TextField(blank=True)
    publication_year = models.IntegerField()
    available_to_borrow = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-publication_year']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('bookclub:book-detail', args=[str(self.pk)])


class BookReview(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    user_reviewer = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='book_reviews',
    )
    anon_reviewer = models.TextField(blank=True)
    title = models.CharField(max_length=255)
    comment = models.TextField()

    def __str__(self):
        reviewer = self.user_reviewer or self.anon_reviewer or 'Anonymous'
        return '{} on {}'.format(reviewer, self.book.title)

    @property
    def reviewer_display(self):
        if self.user_reviewer:
            return self.user_reviewer.display_name
        return self.anon_reviewer or 'Anonymous'


class Bookmark(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='bookmarks',
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='bookmarks',
    )
    date_bookmarked = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ['profile', 'book']

    def __str__(self):
        return '{} bookmarked {}'.format(self.profile, self.book)


class Borrow(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='borrows',
    )
    borrower = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='borrows',
    )
    name = models.CharField(max_length=255, blank=True)
    date_borrowed = models.DateField()
    date_to_return = models.DateField()

    def save(self, *args, **kwargs):
        if self.date_borrowed and not self.date_to_return:
            self.date_to_return = self.date_borrowed + timedelta(weeks=2)
        super().save(*args, **kwargs)

    def __str__(self):
        who = self.borrower or self.name or 'Unknown'
        return '{} borrowed {}'.format(who, self.book)
