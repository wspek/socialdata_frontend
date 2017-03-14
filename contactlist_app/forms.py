from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from crispy_forms.bootstrap import (FormActions)

MEDIA_CHOICES = (
    ('FACEBOOK', 'Facebook'),
    ('LINKEDIN', 'LinkedIn'),
)


class AccountForm(forms.Form):
    user_name = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    social_network = forms.ChoiceField(MEDIA_CHOICES, required=False)
    social_network.disabled = True  # TODO: Add more social networks and dekete

    helper = FormHelper()
    helper.form_id = 'id-AccountForm'
    helper.form_method = 'POST'
    helper.layout = Layout(
        Field('user_name', css_class='input-sm'),
        Field('password', css_class='input-sm'),
        Field('social_network', css_class='btn-secondary'),
        FormActions(Submit('continue', 'Continue', css_class='btn-default'))
    )


class ProfileForm(forms.Form):
    profile_id = forms.CharField(max_length=100)

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
        Field('profile_id', css_class='input-sm'),
        FormActions(Submit('get_contacts', 'Get contacts', css_class='btn-default'))
    )
