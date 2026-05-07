from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms.models import inlineformset_factory
from django.db import transaction
from django.db.models import Case, When, IntegerField, Value, Sum
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404

from accounts.models import Profile
from .models import Commission, Job, JobApplication


JobFormSet = inlineformset_factory(
    Commission,
    Job,
    fields=['role', 'manpower_required', 'status'],
    extra=1,
    can_delete=True
)


class CommissionListView(ListView):
    model = Commission
    template_name = 'commissions/commission_list.html'
    context_object_name = 'commissions'

    def get_queryset(self):
        status_order = Case(
            When(status='Open', then=Value(0)),
            When(status='Full', then=Value(1)),
            default=Value(2),
            output_field=IntegerField(),
        )

        return Commission.objects.annotate(
            status_rank=status_order
        ).order_by('status_rank', '-created_on')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            profile = getattr(user, 'profile', None)
            if profile is None:
                profile = Profile.objects.filter(user=user).first()

            if profile:
                created_commissions = Commission.objects.filter(maker=profile)
                applied_commissions = Commission.objects.filter(
                    jobs__applications__applicant=profile
                ).distinct()

                excluded_ids = list(created_commissions.values_list('id', flat=True)) + \
                               list(applied_commissions.values_list('id', flat=True))

                context['created_commissions'] = created_commissions
                context['applied_commissions'] = applied_commissions
                context['commissions'] = context['commissions'].exclude(id__in=excluded_ids)
            else:
                context['created_commissions'] = Commission.objects.none()
                context['applied_commissions'] = Commission.objects.none()
        else:
            context['created_commissions'] = Commission.objects.none()
            context['applied_commissions'] = Commission.objects.none()

        return context


class CommissionDetailView(DetailView):
    model = Commission
    template_name = 'commissions/commission_detail.html'
    context_object_name = 'commission'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        commission = self.object
        user = self.request.user

        jobs = commission.jobs.all()

        total_manpower = jobs.aggregate(total=Sum('manpower_required'))['total'] or 0
        accepted_count = JobApplication.objects.filter(
            job__commission=commission,
            status='Accepted'
        ).count()

        job_full = {}
        user_applied_to = {}
        
        for job in jobs:
            accepted_for_job = job.applications.filter(status='Accepted').count()
            job_full[job.id] = accepted_for_job >= job.manpower_required
            
            if user.is_authenticated:
                profile = getattr(user, 'profile', None)
                if profile is None:
                    profile = Profile.objects.filter(user=user).first()
                user_applied_to[job.id] = JobApplication.objects.filter(
                    job=job,
                    applicant=profile
                ).exists()

        profile = None
        if user.is_authenticated:
            profile = getattr(user, 'profile', None)
            if profile is None:
                profile = Profile.objects.filter(user=user).first()

        context.update({
            'jobs': jobs,
            'total_manpower': total_manpower,
            'open_manpower': max(total_manpower - accepted_count, 0),
            'job_full': job_full,
            'user_applied_to': user_applied_to,
            'is_owner': user.is_authenticated and profile is not None and commission.maker == profile,
            'can_apply': user.is_authenticated,
        })
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        commission = self.get_object()
        job_pk = request.POST.get('job_id')
        
        try:
            job = commission.jobs.get(pk=job_pk)
        except Job.DoesNotExist:
            return redirect('commissions:commission_detail', pk=commission.pk)

        profile = getattr(request.user, 'profile', None)
        if profile is None:
            profile = Profile.objects.filter(user=request.user).first()

        if JobApplication.objects.filter(job=job, applicant=profile).exists():
            return redirect('commissions:commission_detail', pk=commission.pk)

        JobApplication.objects.create(job=job, applicant=profile, status='Pending')

        return redirect('commissions:commission_detail', pk=commission.pk)


class CommissionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Commission
    template_name = 'commissions/commission_form.html'
    fields = ['title', 'description', 'type', 'people_required', 'status']

    def test_func(self):
        profile = getattr(self.request.user, 'profile', None)
        if profile is None:
            profile = Profile.objects.filter(user=self.request.user).first()
        return profile is not None and profile.role == 'Commission Maker'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['job_formset'] = JobFormSet(self.request.POST, instance=self.object)
        else:
            context['job_formset'] = JobFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        job_formset = context['job_formset']
        
        profile = getattr(self.request.user, 'profile', None)
        if profile is None:
            profile = Profile.objects.filter(user=self.request.user).first()
        
        form.instance.maker = profile

        with transaction.atomic():
            response = super().form_valid(form)
            if job_formset.is_valid():
                job_formset.instance = self.object
                job_formset.save()
                return response
            else:
                return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('commissions:commission_detail', kwargs={'pk': self.object.pk})


class CommissionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Commission
    template_name = 'commissions/commission_form.html'
    fields = ['title', 'description', 'type', 'people_required', 'status']

    def test_func(self):
        profile = getattr(self.request.user, 'profile', None)
        if profile is None:
            profile = Profile.objects.filter(user=self.request.user).first()
        
        commission = self.get_object()
        return profile is not None and profile.role == 'Commission Maker' and commission.maker == profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['job_formset'] = JobFormSet(self.request.POST, instance=self.object)
        else:
            context['job_formset'] = JobFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        job_formset = context['job_formset']

        with transaction.atomic():
            response = super().form_valid(form)
            if job_formset.is_valid():
                job_formset.instance = self.object
                job_formset.save()

                all_full = not self.object.jobs.exclude(status='Full').exists()
                if all_full:
                    self.object.status = 'Full'
                    self.object.save(update_fields=['status'])
                
                return response
            else:
                return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('commissions:commission_detail', kwargs={'pk': self.object.pk})
