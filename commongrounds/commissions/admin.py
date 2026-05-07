from django.contrib import admin

from .models import Commission, CommissionType, Job, JobApplication


class CommissionTypeAdmin(admin.ModelAdmin):
    model = CommissionType
    search_fields = ['name']
    list_display = ['name', 'description']


class JobAdmin(admin.ModelAdmin):
    model = Job
    search_fields = ['role', 'commission__title']
    list_display = ['role', 'commission', 'manpower_required', 'status']


class JobApplicationAdmin(admin.ModelAdmin):
    model = JobApplication
    search_fields = ['job__role', 'applicant__username']
    list_display = ['job', 'applicant', 'status', 'applied_on']
    readonly_fields = ['applied_on']


class CommissionAdmin(admin.ModelAdmin):
    model = Commission
    search_fields = ['title', 'description']
    list_display = ['title', 'maker', 'people_required', 'status', 'created_on', 'updated_on']
    readonly_fields = ['created_on', 'updated_on']


admin.site.register(CommissionType, CommissionTypeAdmin)
admin.site.register(Commission, CommissionAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(JobApplication, JobApplicationAdmin)
