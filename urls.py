from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from apps.general import views as general
from apps.scheduling import views as scheduling_views
from apps.juliana.views import juliana

admin.autodiscover()

urlpatterns = [
    # Root
    url(r'^$', scheduling_views.overview),

    # Apps
    url(r'^billing/', include('apps.billing.urls')),
    url(r'^juliana/(?P<pk>\d+)/$', juliana),
    url(r'^organization/', include('apps.organization.urls')),
    url(r'^profile/', include('apps.profile.urls')),
    url(r'^scheduling/', include('apps.scheduling.urls')),
    url(r'^ical$', scheduling_views.ical),
    url(r'^ical/(?P<ical_id>\w+)$', scheduling_views.personal_ical, name='ical'),

    url(r'^api/', include('api.urls')),

    # "Static" general
    url(r'^about/$', general.about),
    url(r'^help/$', general.help_view),
    url(r'^login/$', general.login, name='login'),
    url(r'^logout/$', general.logout, name='logout'),
    url(r'^register/$', general.register),
    url(r'^change_current_organization/(?P<organization>[-\w]+)/$',
        general.change_current_organization),

    # Django Admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Internationalization
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # Robots
    url(r'^robots\.txt$',
        TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]
