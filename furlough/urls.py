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
    url(r'^/?$', 'furlough.views.index', name='index'),
    url(r'^ajax/timeline.json$', 'furlough.views.timeline_json'),
    url(r'^ajax/offtime/(\d+).html$', 'furlough.views.offtime'),
    url(r'^ajax/offtime/(\d+)/(\w+).html$', 'furlough.views.offtime'),
    url(r'^ajax/person_detail/(\d+).html$', 'furlough.views.person_detail'),

    url(r'^person.html$', 'furlough.views.person', name='person'),
    url(r'^settings.html$', 'furlough.views.settings', name='settings'),

    url(r'^(person|settings)/(capability|offtime_type|person)/(edit|delete)/(\d+)\.html$',
        'furlough.views.change_api'),
    url(r'^person_capability/delete/p(\d+)c(\d+)$',
        'furlough.views.delete_person_capability'),
    url(r'^add_offtime.html$', 'furlough.views.add_offtime'),
)

