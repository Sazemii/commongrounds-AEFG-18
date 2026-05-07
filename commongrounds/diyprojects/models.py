from django.db import models
from django.urls import reverse

from accounts.models import Profile


class ProjectCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ['name']
        verbose_name = 'Project category'
        verbose_name_plural = 'Project categories'

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.SET_NULL,
        null=True,
    )
    creator = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_projects',
    )
    description = models.TextField()
    materials = models.TextField()
    steps = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('diyprojects:project-detail', args=[str(self.pk)])


class Favorite(models.Model):
    STATUS_BACKLOG = 'Backlog'
    STATUS_TODO = 'To-Do'
    STATUS_DONE = 'Done'
    STATUS_CHOICES = [
        (STATUS_BACKLOG, 'Backlog'),
        (STATUS_TODO, 'To-Do'),
        (STATUS_DONE, 'Done'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='favorite_projects',
    )
    date_favorited = models.DateField(auto_now_add=True)
    project_status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_BACKLOG,
    )

    class Meta:
        unique_together = ['profile', 'project']

    def __str__(self):
        return '{} favorited {}'.format(self.profile, self.project)


class ProjectReview(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    reviewer = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='project_reviews',
    )
    comment = models.TextField()
    image = models.ImageField(upload_to='diyprojects/reviews/', blank=True, null=True)

    def __str__(self):
        return '{} reviewed {}'.format(self.reviewer, self.project)


class ProjectRating(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='ratings',
    )
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='project_ratings',
    )
    score = models.IntegerField()

    class Meta:
        unique_together = ['profile', 'project']

    def __str__(self):
        return '{} rated {} ({}/10)'.format(self.profile, self.project, self.score)
