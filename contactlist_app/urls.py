from django.conf.urls import url
from . import views

app_name = 'contactlist_app'
urlpatterns = [
    # ex: /contacts/
    url(r'^$', views.account, name='account'),
    # ex: /contacts/choice
    url(r'^action/$', views.action, name='action'),
    # ex: /contacts/profile
    url(r'^profile/$', views.get_contacts, name='contacts'),
    # ex: /contacts/profile/poll_state
    url(r'^profile/poll_state/$', views.poll_state, name='poll'),
    # ex: /contacts/mutuals
    url(r'^mutuals/$', views.get_mutual_contacts, name='mutuals'),
    # ex: /contacts/profile/poll_state
    url(r'^mutuals/poll_state/$', views.poll_state, name='poll'),
    # ex: /contacts/download
    url(r'^download/$', views.download, name='download'),
]