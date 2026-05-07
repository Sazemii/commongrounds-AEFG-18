"""Repository pattern for the DIY Projects app.

Direct ORM calls to Project (e.g. Project.objects.all()) must live ONLY in
this module. Views interact with projects exclusively through an instance of
ProjectRepository.
"""

from .models import Project


class ProjectRepository:
    """Single point of access to the Project ORM."""

    def get_all(self):
        return Project.objects.all()

    def get_by_category(self, category_name):
        return Project.objects.filter(category__name=category_name)

    def get_recent(self, n):
        return Project.objects.order_by('-created_on')[:n]

    def get_by_id(self, id):
        try:
            return Project.objects.get(pk=id)
        except Project.DoesNotExist:
            return None

    def get_by_creator(self, profile):
        return Project.objects.filter(creator=profile)

    def get_favorited_by(self, profile):
        return Project.objects.filter(favorites__profile=profile).distinct()

    def get_reviewed_by(self, profile):
        return Project.objects.filter(reviews__reviewer=profile).distinct()
