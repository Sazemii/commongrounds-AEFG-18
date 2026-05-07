from django.contrib import admin

from .models import Favorite, Project, ProjectCategory, ProjectRating, ProjectReview


class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'creator', 'created_on')
    list_filter = ('category',)
    search_fields = ('title', 'description')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('profile', 'project', 'project_status', 'date_favorited')
    list_filter = ('project_status',)


class ProjectReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'project')


class ProjectRatingAdmin(admin.ModelAdmin):
    list_display = ('profile', 'project', 'score')


admin.site.register(ProjectCategory, ProjectCategoryAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ProjectReview, ProjectReviewAdmin)
admin.site.register(ProjectRating, ProjectRatingAdmin)
