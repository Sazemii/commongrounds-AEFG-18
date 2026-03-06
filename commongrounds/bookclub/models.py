from django.db import models
from django.urls import reverse


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
    author = models.CharField(max_length=255)
    publication_year = models.IntegerField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-publication_year']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('bookclub:book-detail', args=[str(self.pk)])
