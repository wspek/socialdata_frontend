from django.conf.urls import url
from . import views

app_name = 'contactlist'
urlpatterns = [
    # ex: /contacts/
    url(r'^$', views.get_contacts(), name='contacts'),
]