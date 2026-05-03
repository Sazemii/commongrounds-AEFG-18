from django.urls import path

from .views import (
    PermissionDeniedView,
    ProfileUpdateView,
    RegisterView,
    contributor_dashboard,
)

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('permission-denied/', PermissionDeniedView.as_view(),
         name='permission-denied'),
    path('contributor-dashboard/', contributor_dashboard,
         name='contributor-dashboard'),
    path('<str:username>/', ProfileUpdateView.as_view(),
         name='profile-update'),
]
