from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from accounts.mixins import RoleRequiredMixin
from accounts.models import Profile

from .forms import BookFormFactory
from .models import Book, Bookmark, BookReview, Borrow


class BookListView(ListView):
    model = Book
    template_name = 'bookclub/book_list.html'
    context_object_name = 'all_books'

    def get_queryset(self):
        qs = Book.objects.all()
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'profile'):
            profile = user.profile
            contributed_ids = list(
                Book.objects.filter(contributor=profile).values_list('pk', flat=True)
            )
            bookmarked_ids = list(
                Bookmark.objects.filter(profile=profile).values_list('book_id', flat=True)
            )
            reviewed_ids = list(
                BookReview.objects.filter(user_reviewer=profile).values_list('book_id', flat=True)
            )
            grouped = set(contributed_ids) | set(bookmarked_ids) | set(reviewed_ids)
            qs = qs.exclude(pk__in=grouped)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'profile'):
            profile = user.profile
            ctx['contributed_books'] = Book.objects.filter(contributor=profile)
            ctx['bookmarked_books'] = Book.objects.filter(
                bookmarks__profile=profile
            ).distinct()
            ctx['reviewed_books'] = Book.objects.filter(
                reviews__user_reviewer=profile
            ).distinct()
        return ctx


class BookDetailView(DetailView):
    model = Book
    template_name = 'bookclub/book_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        review_form_cls = BookFormFactory.get_form('review')
        ctx['review_form'] = review_form_cls()
        ctx['reviews'] = self.object.reviews.all()
        ctx['bookmark_count'] = self.object.bookmarks.count()
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'profile'):
            ctx['is_owner'] = self.object.contributor_id == user.profile.pk
            ctx['is_bookmarked'] = self.object.bookmarks.filter(
                profile=user.profile
            ).exists()
        else:
            ctx['is_owner'] = False
            ctx['is_bookmarked'] = False
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        review_form_cls = BookFormFactory.get_form('review')
        form = review_form_cls(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = self.object
            if request.user.is_authenticated and hasattr(request.user, 'profile'):
                review.user_reviewer = request.user.profile
            else:
                review.anon_reviewer = 'Anonymous'
            review.save()
            return redirect(self.object.get_absolute_url())
        ctx = self.get_context_data()
        ctx['review_form'] = form
        return render(request, self.template_name, ctx)


class BookCreateView(RoleRequiredMixin, CreateView):
    model = Book
    template_name = 'bookclub/book_form.html'
    required_role = Profile.ROLE_BOOK_CONTRIBUTOR

    def get_form_class(self):
        return BookFormFactory.get_form('contribute')

    def form_valid(self, form):
        book = form.save(commit=False)
        book.contributor = self.request.user.profile
        book.save()
        self.object = book
        return redirect(book.get_absolute_url())


class BookUpdateView(RoleRequiredMixin, UpdateView):
    model = Book
    template_name = 'bookclub/book_form.html'
    required_role = Profile.ROLE_BOOK_CONTRIBUTOR

    def get_form_class(self):
        return BookFormFactory.get_form('update')

    def get_success_url(self):
        return self.object.get_absolute_url()


class BookBorrowView(DetailView):
    model = Book
    template_name = 'bookclub/book_borrow.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        form_cls = BookFormFactory.get_form('borrow')
        initial = {}
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'profile'):
            initial['name'] = user.profile.display_name
        ctx['borrow_form'] = form_cls(initial=initial, user=user)
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_cls = BookFormFactory.get_form('borrow')
        form = form_cls(request.POST, user=request.user)
        if form.is_valid():
            borrow = form.save(commit=False)
            borrow.book = self.object
            if request.user.is_authenticated and hasattr(request.user, 'profile'):
                borrow.borrower = request.user.profile
                if not borrow.name:
                    borrow.name = request.user.profile.display_name
            borrow.save()
            self.object.available_to_borrow = False
            self.object.save(update_fields=['available_to_borrow'])
            return redirect(self.object.get_absolute_url())
        ctx = self.get_context_data()
        ctx['borrow_form'] = form
        return render(request, self.template_name, ctx)


def bookmark_toggle(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method != 'POST':
        return redirect('bookclub:book-detail', pk=pk)
    try:
        book = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        raise Http404
    profile = request.user.profile
    existing = Bookmark.objects.filter(profile=profile, book=book)
    if existing.exists():
        existing.delete()
    else:
        Bookmark.objects.create(profile=profile, book=book)
    return redirect('bookclub:book-detail', pk=pk)
