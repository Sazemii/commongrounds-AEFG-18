from django.urls import path
from .views import CommissionListView, CommissionDetailView

app_name = 'commissions'

urlpatterns = [
    path('requests',
         CommissionListView.as_view(),
         name='commission_list'),
    path('request/<int:pk>',
         CommissionDetailView.as_view(),
         name='commission_detail'
         )
    
]

