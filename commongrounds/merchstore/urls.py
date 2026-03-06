from django.urls import path
from .views import ProductListView, ProductDetailView

urlpatterns = [
    path('items',
         ProductListView.as_view(),
         name='items_list'),
    path('item/<int:pk>',
         ProductDetailView.as_view(),
         name='item_detail'),
]

app_name = "merchstore"
