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
    url(r'^timeline.json$', 'furlough_tracker.views.timeline_json'),

    url(r'^person.html$', 'furlough_tracker.views.person', name='person'),
    url(r'^settings.html$', 'furlough_tracker.views.settings', name='settings'),

    url(r'^(person|settings)/(capability|offtime_type|person)/(edit|delete)/(\d+)\.html$',
        'furlough_tracker.views.change_api'),
    url(r'^person_capability/delete/p(\d+)c(\d+)$',
        'furlough_tracker.views.delete_person_capability'),
)

