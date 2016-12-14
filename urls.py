from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from apps.consumption.views import dcf, complete_dcf
from apps.general import views as general_views
from apps.juliana.views import juliana
from apps.scheduling import views as scheduling_views

urlpatterns = [
    # Root
    url(r'^$', scheduling_views.overview, name='root'),

    # Short urls to 'subsystems'
    url(r'^dcf/(?P<pk>\d+)/$', dcf, name='dcf'),
    url(r'^dcf/(?P<pk>\d+)/check/$', complete_dcf, name='dcf-complete'),
    url(r'^juliana/(?P<pk>\d+)/$', juliana, name='juliana'),

    # Apps
    url(r'^billing/', include('apps.billing.urls')),
    url(r'^consumption/', include('apps.consumption.urls')),
    url(r'^organization/', include('apps.organization.urls')),
    url(r'^profile/', include('apps.profile.urls')),
    url(r'^scheduling/', include('apps.scheduling.urls')),
    url(r'^ical$', scheduling_views.ical),
    url(r'^ical/(?P<ical_id>[^/]+)$', scheduling_views.personal_ical, name='ical'),

    url(r'^api/', include('api.urls')),

    # "Static" general_views
    url(r'^about/$', general_views.about, name='about'),
    url(r'^help/$', general_views.help, name='help'),
    url(r'^login/$', general_views.login, name='login'),
    url(r'^logout/$', general_views.logout, name='logout'),
    url(r'^register/$', general_views.register, name='register'),
    url(r'^change_current_organization/(?P<organization>[-\w]+)/$',
        general_views.change_current_organization, name='change-current-organization'),

    # Django Admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Internationalization
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # Robots
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

# Debug toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
