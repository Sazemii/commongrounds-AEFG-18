from django.urls import path

from .views import (
    ProjectCreateView,
    ProjectDetailView,
    ProjectListView,
    ProjectUpdateView,
    ProjectReviewView,
    ProjectRatingView,
)

app_name = 'projects'

urlpatterns = [
    path('projects', ProjectListView.as_view(), name='project_list'),
    path('project/<int:pk>', ProjectDetailView.as_view(), name='project_detail'),
    path('project/add', ProjectCreateView.as_view(), name='project_add'),
    path('project/<int:pk>/edit',
         ProjectUpdateView.as_view(), name='project_edit'),
    path('project/review', ProjectReviewView.as_view(), name='project_form'),
    path('project/rating', ProjectRatingView.as_view(), name='project_form'),
]
