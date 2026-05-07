from django.urls import path

from .views import (
    ProjectCreateView,
    ProjectDetailView,
    ProjectListView,
    ProjectUpdateView,
)

app_name = 'commissions'

urlpatterns = [
    path('requests', ProjectListView.as_view(), name='commission_list'),
    path('request/<int:pk>', ProjectDetailView.as_view(), name='commission_detail'),
    path('request/add', ProjectCreateView.as_view(), name='commission_add'),
    path('request/<int:pk>/edit',
         ProjectUpdateView.as_view(), name='commission_edit'),
]
