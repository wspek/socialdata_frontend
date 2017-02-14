from django import forms

MEDIA_CHOICES = (
    ('FACEBOOK', 'Facebook'),
    ('LINKEDIN', 'LinkedIn'),
)


class AccountForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    medium = forms.ChoiceField(MEDIA_CHOICES)


class ProfileForm(forms.Form):
    profile_id = forms.CharField(max_length=100)
