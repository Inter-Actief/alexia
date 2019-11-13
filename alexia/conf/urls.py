import djangosaml2
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView, TemplateView

from alexia.apps.billing.views import JulianaView
from alexia.apps.consumption.views import complete_dcf, dcf
from alexia.apps.general import views as general_views
from alexia.apps.scheduling import views as scheduling_views

urlpatterns = [
    # Root
    url(r'^$', RedirectView.as_view(pattern_name='event-list', permanent=True)),

    # Short urls to 'subsystems'
    url(r'^dcf/(?P<pk>\d+)/$', dcf, name='dcf'),
    url(r'^dcf/(?P<pk>\d+)/check/$', complete_dcf, name='dcf-complete'),
    url(r'^juliana/(?P<pk>\d+)/$', JulianaView.as_view(), name='juliana'),

    # Apps
    url(r'^billing/', include('alexia.apps.billing.urls')),
    url(r'^consumption/', include('alexia.apps.consumption.urls')),
    url(r'^organization/', include('alexia.apps.organization.urls')),
    url(r'^profile/', include('alexia.apps.profile.urls')),
    url(r'^scheduling/', include('alexia.apps.scheduling.urls')),
    url(r'^ical$', scheduling_views.ical),
    url(r'^ical/(?P<ical_id>[^/]+)$', scheduling_views.personal_ical, name='ical'),

    url(r'^api/', include('alexia.api.urls')),

    # "Static" general_views
    url(r'^about/$', general_views.AboutView.as_view(), name='about'),
    url(r'^help/$', general_views.HelpView.as_view(), name='help'),
    url(r'^login_complete/$', general_views.login_complete, name='login_complete'),
    url(r'^login/$', general_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^register/$', general_views.RegisterView.as_view(), name='register'),
    url(r'^change_current_organization/(?P<slug>[-\w]+)/$',
        general_views.ChangeCurrentOrganizationView.as_view(), name='change-current-organization'),

    # SAML2 SP
    url(r'^saml2sp/', include('djangosaml2.urls')),

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
        # SAML test URLs
        url(r'^saml2test/', djangosaml2.views.echo_attributes),
    ]
    # Translation application for development
    urlpatterns += [
        url(r'^translations/', include('rosetta.urls'), name='translations')
    ]
