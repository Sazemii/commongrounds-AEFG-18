from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from bookclub.models import Book
from commissions.models import Commission
from diyprojects.models import Project
from localevents.models import Event
from merchstore.models import Product
from .decorators import role_required
from .forms import ProfileUpdateForm, RegisterForm
from .models import Profile


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('homepage:home')

    def form_valid(self, form):
        user = form.save()
        Profile.objects.create(
            user=user,
            display_name=form.cleaned_data['display_name'],
            email_address=form.cleaned_data['email_address'],
        )
        login(self.request, user)
        return redirect(self.success_url)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_form.html'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        if username != self.request.user.username:
            raise Http404
        return self.request.user.profile

    def get_success_url(self):
        return self.object.get_absolute_url() + '?saved=1'


class PermissionDeniedView(TemplateView):
    template_name = 'accounts/permission_denied.html'


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profile
        context['books'] = Book.objects.filter(contributor=profile)
        context['events'] = Event.objects.filter(organizer=profile)
        context['commissions'] = Commission.objects.filter(maker=profile)
        context['products'] = Product.objects.filter(owner=profile)
        context['projects'] = Project.objects.filter(creator=profile)
        return context


@role_required(Profile.ROLE_BOOK_CONTRIBUTOR)
def contributor_dashboard(request):
    contributed_books = []
    try:
        contributed_books = list(
            request.user.profile.book_set.all()
        )
    except AttributeError:
        contributed_books = []
    return render(
        request,
        'accounts/contributor_dashboard.html',
        {'books': contributed_books},
    )
