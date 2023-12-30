from django import forms

class RatingForm(forms.Form):
    rating = forms.IntegerField(label='Rating', min_value=1, max_value=5)
