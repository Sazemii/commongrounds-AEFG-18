from django.contrib import admin
from .models import ProjectCategory, Project

class ProjectCategoryInline(admin.TabularInline):
    model = ProjectCategory
    extra = 1

class ProjectCategoryAdmin(admin.ModelAdmin):
    inlines = [ProjectCategoryInline]

class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1

class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectCategoryInline]

admin.site.register(ProjectCategoryInline, ProjectCategoryAdmin)
admin.site.register(ProjectInline, ProjectAdmin)
# Register your models here.
