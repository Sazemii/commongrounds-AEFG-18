from django.urls import path

from .views import (
    BookBorrowView,
    BookCreateView,
    BookDetailView,
    BookListView,
    BookUpdateView,
    bookmark_toggle,
)


app_name = "bookclub"

urlpatterns = [
    path('books', BookListView.as_view(), name='book-list'),
    path('book/add', BookCreateView.as_view(), name='book-create'),
    path('book/<int:pk>', BookDetailView.as_view(), name='book-detail'),
    path('book/<int:pk>/edit', BookUpdateView.as_view(), name='book-update'),
    path('book/<int:pk>/borrow', BookBorrowView.as_view(), name='book-borrow'),
    path('book/<int:pk>/bookmark', bookmark_toggle, name='book-bookmark'),
]
