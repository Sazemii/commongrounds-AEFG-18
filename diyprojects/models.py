from django.db import models
from django.urls import reverse

class ProjectCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name 

class Project(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        PostCategory,
        on_delete=models.NULL,
        null=True,
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
        return reverse('diyprojects:project_detail', args=[str(self.pk)])


# Create your models here.
