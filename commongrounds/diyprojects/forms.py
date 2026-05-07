from django import forms

from .models import Project, ProjectRating, ProjectReview


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'category', 'description', 'materials', 'steps']


class ProjectReviewForm(forms.ModelForm):
    class Meta:
        model = ProjectReview
        fields = ['comment', 'image']


class ProjectRatingForm(forms.ModelForm):
    score = forms.IntegerField(min_value=1, max_value=10)

    class Meta:
        model = ProjectRating
        fields = ['score']
