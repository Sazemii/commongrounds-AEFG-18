from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .models import Project


class ProjectListView(ListView):
    model = Project
    template_name = 'diyprojects/project_list.html'


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'diyprojects/project_detail.html'
