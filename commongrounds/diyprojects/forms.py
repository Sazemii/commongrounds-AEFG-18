from django import forms


class ReviewRatingForm(forms.Form):
    score = forms.IntegerField(
        min_value=1,
        max_value=10,
        label="Rating (1-10)"
    )
    comment = forms.CharField(
        widget=forms.Textarea,
        label="Your Review"
    )
    image = forms.ImageField(
        required=False,
        label="Upload Image"
    )
