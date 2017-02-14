from django.conf.urls import url
from . import views

app_name = 'contactlist'
urlpatterns = [
    # ex: /contacts/
    url(r'^$', views.account, name='account'),
    # ex: /contacts/profile
    url(r'^profile/$', views.get_contacts, name='contacts'),
    # ex: /contacts/download
    url(r'^download/$', views.download, name='download'),
]