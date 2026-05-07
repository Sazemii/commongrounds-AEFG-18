from django.urls import path

from .views import (
    CartView,
    ProductCreateView,
    ProductDetailView,
    ProductListView,
    ProductUpdateView,
    TransactionListView,
    complete_pending_transaction,
)

app_name = "merchstore"

urlpatterns = [
    path('items', ProductListView.as_view(), name='items_list'),
    path('item/add', ProductCreateView.as_view(), name='item_create'),
    path('item/<int:pk>', ProductDetailView.as_view(), name='item_detail'),
    path('item/<int:pk>/edit', ProductUpdateView.as_view(), name='item_update'),
    path('cart', CartView.as_view(), name='cart'),
    path('transactions', TransactionListView.as_view(), name='transactions'),
    path('checkout/complete', complete_pending_transaction, name='checkout_complete'),
]
