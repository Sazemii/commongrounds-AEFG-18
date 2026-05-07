from django.urls import path
from .views import (
    ProductListView, 
    ProductDetailView, 
    ProductCreateView, 
    ProductUpdateView, 
    CartView, 
    TransactionListView
)

urlpatterns = [
    path('items',
         ProductListView.as_view(),
         name='product-list'),
    path('item/<int:pk>',
         ProductDetailView.as_view(),
         name='product-detail'),
    path('item/add',
         ProductCreateView.as_view(),
         name='product-create'),
    path('item/<int:pk>/edit',
         ProductUpdateView.as_view(),
         name='product-update'),
    path('cart',
         CartView.as_view(),
         name='cart'),
    path('transactions',
         TransactionListView.as_view(),
         name='transactions_list'),
]

app_name = "merchstore"
