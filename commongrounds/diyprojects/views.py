from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from accounts.mixins import RoleRequiredMixin
from accounts.models import Profile

from .forms import ProjectForm, ProjectRatingForm, ProjectReviewForm
from .models import Favorite, ProjectRating, ProjectReview
from .repositories import ProjectRepository


class ProjectListView(ListView):
    template_name = 'diyprojects/project_list.html'
    context_object_name = 'all_projects'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repository = ProjectRepository()

    def get_queryset(self):
        qs = self.repository.get_all()
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'profile'):
            profile = user.profile
            created_ids = list(self.repository.get_by_creator(profile).values_list('pk', flat=True))
            favorited_ids = list(self.repository.get_favorited_by(profile).values_list('pk', flat=True))
            reviewed_ids = list(self.repository.get_reviewed_by(profile).values_list('pk', flat=True))
            grouped = set(created_ids) | set(favorited_ids) | set(reviewed_ids)
            qs = qs.exclude(pk__in=grouped)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'profile'):
            profile = user.profile
            ctx['created_projects'] = self.repository.get_by_creator(profile)
            ctx['favorited_projects'] = self.repository.get_favorited_by(profile)
            ctx['reviewed_projects'] = self.repository.get_reviewed_by(profile)
        return ctx


class ProjectDetailView(DetailView):
    template_name = 'diyprojects/project_detail.html'
    context_object_name = 'project'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repository = ProjectRepository()

    def get_object(self, queryset=None):
        project = self.repository.get_by_id(self.kwargs.get('pk'))
        if project is None:
            raise Http404
        return project

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        project = self.object
        ratings = project.ratings.all()
        avg = ratings.aggregate(avg=Avg('score'))['avg']
        ctx['average_rating'] = round(avg, 1) if avg is not None else None
        ctx['rating_count'] = ratings.count()
        ctx['favorite_count'] = project.favorites.count()
        ctx['reviews'] = project.reviews.all()
        ctx['review_form'] = ProjectReviewForm()
        ctx['rating_form'] = ProjectRatingForm()
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'profile'):
            ctx['is_owner'] = project.creator_id == user.profile.pk
            ctx['is_favorited'] = project.favorites.filter(profile=user.profile).exists()
        else:
            ctx['is_owner'] = False
            ctx['is_favorited'] = False
        return ctx

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        self.object = self.get_object()
        action = request.POST.get('action')
        if action == 'rate':
            form = ProjectRatingForm(request.POST)
            if form.is_valid():
                profile = request.user.profile
                ProjectRating.objects.update_or_create(
                    project=self.object,
                    profile=profile,
                    defaults={'score': form.cleaned_data['score']},
                )
                return redirect(self.object.get_absolute_url())
            ctx = self.get_context_data()
            ctx['rating_form'] = form
            return render(request, self.template_name, ctx)
        # default: review submission
        form = ProjectReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.project = self.object
            review.reviewer = request.user.profile
            review.save()
            return redirect(self.object.get_absolute_url())
        ctx = self.get_context_data()
        ctx['review_form'] = form
        return render(request, self.template_name, ctx)


class ProjectCreateView(RoleRequiredMixin, CreateView):
    form_class = ProjectForm
    template_name = 'diyprojects/project_form.html'
    required_role = Profile.ROLE_PROJECT_CREATOR

    def form_valid(self, form):
        project = form.save(commit=False)
        project.creator = self.request.user.profile
        project.save()
        self.object = project
        return redirect(project.get_absolute_url())


class ProjectUpdateView(RoleRequiredMixin, UpdateView):
    form_class = ProjectForm
    template_name = 'diyprojects/project_form.html'
    required_role = Profile.ROLE_PROJECT_CREATOR

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repository = ProjectRepository()

    def get_object(self, queryset=None):
        project = self.repository.get_by_id(self.kwargs.get('pk'))
        if project is None:
            raise Http404
        return project

    def get_success_url(self):
        return self.object.get_absolute_url()


@login_required
def favorite_toggle(request, pk):
    repository = ProjectRepository()
    if request.method != 'POST':
        return redirect('diyprojects:project-detail', pk=pk)
    project = repository.get_by_id(pk)
    if project is None:
        raise Http404
    profile = request.user.profile
    existing = Favorite.objects.filter(profile=profile, project=project)
    if existing.exists():
        existing.delete()
    else:
        Favorite.objects.create(profile=profile, project=project)
    return redirect('diyprojects:project-detail', pk=pk)
