from datetime import date, timedelta

from django import forms

from .models import Book, BookReview, Borrow


class BookReviewForm(forms.ModelForm):
    class Meta:
        model = BookReview
        fields = ['title', 'comment']


class BookContributeForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title',
            'genre',
            'author',
            'synopsis',
            'publication_year',
            'available_to_borrow',
        ]


class BookUpdateForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title',
            'genre',
            'author',
            'synopsis',
            'publication_year',
            'available_to_borrow',
        ]


class BookBorrowForm(forms.ModelForm):
    class Meta:
        model = Borrow
        fields = ['name', 'date_borrowed']
        widgets = {
            'date_borrowed': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user and user.is_authenticated:
            self.fields['name'].required = False
            self.fields['name'].widget = forms.HiddenInput()
        if not self.initial.get('date_borrowed'):
            self.initial['date_borrowed'] = date.today()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.date_borrowed:
            instance.date_to_return = instance.date_borrowed + timedelta(weeks=2)
        if commit:
            instance.save()
        return instance


class BookFormFactory:
    """Factory Method: returns the appropriate form class for a given context."""

    @classmethod
    def get_form(cls, context):
        if context == 'review':
            return BookReviewForm
        if context == 'contribute':
            return BookContributeForm
        if context == 'update':
            return BookUpdateForm
        if context == 'borrow':
            return BookBorrowForm
        raise ValueError('Unknown form context: {}'.format(context))
