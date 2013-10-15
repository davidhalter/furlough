from django.contrib import admin
from django.conf.urls.defaults import patterns, include, url

# See: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#hooking-adminsite-instances-into-your-urlconf
admin.autodiscover()

# See: https://docs.djangoproject.com/en/dev/topics/http/urls/
urlpatterns = patterns('',
    # Admin panel and documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Authentification
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),

    # Password reset urls
    url(r'', include('password_reset.urls')),

    # Main page for your app. Change or modify this.
    url(r'^/?$', 'main.views.index', name='index'),
    url(r'^ajax/timeline.json$', 'main.views.timeline_json'),
    url(r'^ajax/offtime/(\d+).html$', 'main.views.offtime'),
    url(r'^ajax/offtime/(\d+)/(\w+).html$', 'main.views.offtime'),
    url(r'^ajax/person_detail/(\d+).html$', 'main.views.person_detail'),

    url(r'^person.html$', 'main.views.person', name='person'),
    url(r'^settings.html$', 'main.views.settings', name='settings'),

    url(r'^(person|settings)/(capability|offtime_type|person)/(edit|delete)/(\d+)\.html$',
        'main.views.change_api'),
    url(r'^person_capability/delete/p(\d+)c(\d+)$', 'main.views.delete_person_capability'),
    url(r'^ajax/add_offtime.html$', 'main.views.modify_offtime'),
    url(r'^ajax/edit_offtime/(\d+).html$', 'main.views.modify_offtime'),
)
