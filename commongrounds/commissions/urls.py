from django.urls import path

from .views import (
    CommissionCreateView,
    CommissionDetailView,
    CommissionListView,
    CommissionUpdateView,
    apply_to_job,
)

app_name = 'commissions'

urlpatterns = [
    path('requests', CommissionListView.as_view(), name='commission_list'),
    path('request/add', CommissionCreateView.as_view(), name='commission_add'),
    path('request/<int:pk>', CommissionDetailView.as_view(), name='commission_detail'),
    path('request/<int:pk>/edit', CommissionUpdateView.as_view(), name='commission_edit'),
    path('request/<int:commission_pk>/apply/<int:job_pk>/', apply_to_job, name='commission_apply_job'),
]

