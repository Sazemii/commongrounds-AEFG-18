from django.contrib import admin

from .models import Commission, CommissionType


class CommissionTypeAdmin(admin.ModelAdmin):
    model = CommissionType
    search_fields = ['name']
    list_display = ['name', 'description']


class CommissionAdmin(admin.ModelAdmin):
    model = Commission
    search_fields = ['title', 'description']
    list_display = ['title', 'people_required', 'created_on', 'updated_on']
    readonly_fields = ['created_on', 'updated_on']


admin.site.register(CommissionType, CommissionTypeAdmin)
admin.site.register(Commission, CommissionAdmin)
