from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class RegisterForm(UserCreationForm):
    display_name = forms.CharField(max_length=63)
    email_address = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'display_name', 'email_address',
                  'password1', 'password2']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['display_name']
