from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from crispy_forms.bootstrap import (FormActions)

MEDIA_CHOICES = (
    ('FACEBOOK', 'Facebook'),
    ('LINKEDIN', 'LinkedIn'),
)

OUTPUTTYPE_CHOICES = (
    ('EXCEL', 'MS Excel 2007-2013 - *.xlsx'),
    ('CSV', 'CSV - *.csv'),
)


class AccountForm(forms.Form):
    user_name = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    social_network = forms.ChoiceField(MEDIA_CHOICES, required=False)
    social_network.disabled = True  # TODO: Add more social networks and delete

    helper = FormHelper()
    helper.form_id = 'id-AccountForm'
    helper.form_method = 'POST'
    helper.layout = Layout(
        Field('user_name', css_class='input-sm'),
        Field('password', css_class='input-sm'),
        Field('social_network', css_class='btn-secondary'),
        FormActions(Submit('continue', 'Continue', css_class='btn-default'))
    )


class ActionForm(forms.Form):
    helper = FormHelper()
    helper.form_id = 'id-ActionForm'
    helper.form_method = 'POST'
    helper.layout = Layout(
        FormActions(Submit('profile', 'Get a contact list for an account', css_class='btn-default'),
                    Submit('mutuals', 'Get mutual contacts between two accounts', css_class='btn-default'))
    )


class ProfileForm(forms.Form):
    profile_id = forms.CharField(max_length=100)
    output_file_type = forms.ChoiceField(OUTPUTTYPE_CHOICES, required=False)
    # file_type.disabled = True  # TODO: Add more social networks and delete

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
        Field('profile_id', css_class='input-sm'),
        Field('output_file_type', css_class='btn-secondary'),
        FormActions(Submit('get_contacts', 'Get contacts', css_class='btn-default'))
    )


class MutualContactsForm(forms.Form):
    profile_id1 = forms.CharField(max_length=100)
    profile_id2 = forms.CharField(max_length=100)
    output_file_type = forms.ChoiceField(OUTPUTTYPE_CHOICES, required=False)

    helper = FormHelper()
    helper.form_id = 'id-MutualContactsForm'
    helper.form_method = 'POST'
    helper.layout = Layout(
        Field('profile_id1', css_class='input-sm'),
        Field('profile_id2', css_class='input-sm'),
        Field('output_file_type', css_class='btn-secondary'),
        FormActions(Submit('get_mutual_contacts', 'Get mutual contacts', css_class='btn-default'))
    )
