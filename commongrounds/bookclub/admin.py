from django.contrib import admin

from .models import Book, BookReview, Bookmark, Borrow, Genre


class BookReviewInline(admin.TabularInline):
    model = BookReview
    extra = 0


class GenreAdmin(admin.ModelAdmin):
    model = Genre
    list_display = ('name',)
    search_fields = ('name',)


class BookAdmin(admin.ModelAdmin):
    model = Book
    list_display = ('title', 'author', 'genre', 'publication_year',
                    'available_to_borrow')
    list_filter = ('genre', 'available_to_borrow')
    search_fields = ('title', 'author')
    inlines = [BookReviewInline]


class BookReviewAdmin(admin.ModelAdmin):
    model = BookReview
    list_display = ('title', 'book', 'reviewer_display')


class BookmarkAdmin(admin.ModelAdmin):
    model = Bookmark
    list_display = ('profile', 'book', 'date_bookmarked')


class BorrowAdmin(admin.ModelAdmin):
    model = Borrow
    list_display = ('book', 'borrower', 'name', 'date_borrowed', 'date_to_return')


admin.site.register(Genre, GenreAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(BookReview, BookReviewAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
admin.site.register(Borrow, BorrowAdmin)
