from django.urls import path

from .views import BookListView, BookDetailView


app_name = "bookclub"

urlpatterns = [
    path('books', BookListView.as_view(), name='book-list'),
    path('book/<int:pk>', BookDetailView.as_view(), name='book-detail'),
]
