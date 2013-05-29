from django.contrib import admin
from django.conf.urls.defaults import patterns, include, url

# See: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#hooking-adminsite-instances-into-your-urlconf
admin.autodiscover()

# See: https://docs.djangoproject.com/en/dev/topics/http/urls/
urlpatterns = patterns('',
    # Admin panel and documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Password reset urls
    url(r'', include('password_reset.urls')),

    # Main page for your app. Change or modify this.
    url(r'^/?$', 'furlough_tracker.views.index', name='index'),
)

