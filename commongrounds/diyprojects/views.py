from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg

from accounts.mixins import RoleRequiredMixin
from accounts.models import Profile

from .models import ProjectCategory, Project, Favorite, ProjectReview, ProjectRating


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


class ProjectUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Project
    template_name = 'diyprojects/project_form.html'


class ProjectRatingView(View):
    template_name = 'diyprojects/project_review_rating_form.html'

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        score = request.POST.get('score')
        if score and request.user.is_authenticated:
            ProjectRating.objects.update_or_create(
                project=project,
                profile=request.user.profile,
                defaults={'score': score}
            )
        return redirect(project.get_absolute_url())


class ProjectReviewView(View):
    template_name = 'diyprojects/project_review_rating_form.html'

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        comment = request.POST.get('comment', '').strip()
        if comment and request.user.is_authenticated:
            ProjectReview.objects.create(
                project=project,
                reviewer=request.user.profile,
                comment=comment,
                image=request.FILES.get('image')
            )
        return redirect(project.get_absolute_url())
