from django.contrib import admin

from .models import Genre, Book


class GenreAdmin(admin.ModelAdmin):
    model = Genre


class BookAdmin(admin.ModelAdmin):
    model = Book


admin.site.register(Genre, GenreAdmin)
admin.site.register(Book, BookAdmin)
