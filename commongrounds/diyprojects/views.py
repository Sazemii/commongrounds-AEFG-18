from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg

from accounts.mixins import RoleRequiredMixin
from accounts.models import Profile

from .forms import ProjectForm, ReviewRatingForm

from .models import Project, Favorite, ProjectReview, ProjectRating


class ProjectListView(ListView):
    model = Project
    template_name = 'diyprojects/project_list.html'
    context_object_name = 'projects'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            profile = user.profile
            context['created_projects'] = Project.objects.filter(
                organizer=profile)
            context['favorited_projects'] = Project.objects.filter(
                favorites__profile=profile)
            context['reviewed_projects'] = Project.objects.filter(
                reviews__reviewer=profile).distinct()

            context['projects'] = Project.objects.exclude(
                pk__in=context['created_projects'],
            ).exclude(
                pk__in=context['favorited_projects'],
            ).exclude(
                pk__in=context['reviewed_projects'],
            )
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'diyprojects/project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        user = self.request.user

        context['avg_rating'] = project.ratings.aggregate(Avg('score'))[
            'score__avg'] or 0
        context['fav_count'] = project.favorites.count()
        context['reviews'] = project.reviews.all()

        if user.is_authenticated:
            profile = user.profile
            context['is_creator'] = project.creator == profile
            context['already_favorited'] = project.favorites.filter(
                profile=profile).exists()
            context['review_rating_form'] = ReviewRatingForm()
        else:
            context['is_creator'] = False
            context['already_favorited'] = False

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user.is_authenticated:
            favorite, created = Favorite.objects.get_or_create(
                project=self.object,
                profile=request.user.profile
            )
        return redirect(self.object.get_absolute_url())


class ProjectCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Project
    template_name = 'diyprojects/project_form.html'
    form_class = ProjectForm
    required_role = ROLE_PROJECT_CREATOR

    def form_valid(self, form):
        response = super().form_valid(form)
        return response


class ProjectUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Project
    template_name = 'diyprojects/project_form.html'
    form_class = ProjectForm
    required_role = ROLE_PROJECT_CREATOR


class ProjectReviewRatingView(View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if not request.user.is_authenticated:
            return redirect('login')

        form = ReviewRatingForm(request.POST, request.FILES)
        if form.is_valid():
            profile = request.user.profile

            ProjectRating.objects.update_or_create(
                project=project,
                profile=profile,
                defaults={'score': form.cleaned_data['score']}
            )

            ProjectReview.objects.create(
                project=project,
                reviewer=profile,
                comment=form.cleaned_data['comment'],
                image=form.cleaned_data.get('image')
            )

        return redirect(project.get_absolute_url())
