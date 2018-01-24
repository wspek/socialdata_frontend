from django.conf.urls import include, url
from django.contrib import admin
from django import http

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