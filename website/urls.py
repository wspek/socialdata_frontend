"""pubcrawler URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django import http
import pdb

urlpatterns = [
    url(r'^contacts/', include('contactlist_app.urls')),
    url(r'^admin/', admin.site.urls),
]


def session_test_1(request):
    request.session['test'] = 'Session Vars Worked!'
    return http.HttpResponseRedirect('done/?session={0}'.format(request.session['test']))


def session_test_2(request):
    return http.HttpResponse('<br>'.join([request.session['test']]))


urlpatterns.append(url(r'^session-test/$', session_test_1))
urlpatterns.append(url(r'^session-test/done/$', session_test_2))