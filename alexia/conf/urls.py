from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import re_path, path
from django.views.generic import RedirectView, TemplateView
from django.views.static import serve

from alexia.apps.billing.views import JulianaView
from alexia.apps.consumption.views import complete_dcf, dcf
from alexia.apps.general import views as general_views
from alexia.apps.scheduling import views as scheduling_views

urlpatterns = [
    # Root
    path(r'', RedirectView.as_view(pattern_name='event-list', permanent=True)),

    # Short urls to 'subsystems'
    path('dcf/<int:pk>/', dcf, name='dcf'),
    path('dcf/<int:pk>/check/', complete_dcf, name='dcf-complete'),
    path('juliana/<int:pk>/', JulianaView.as_view(), name='juliana'),

    # Apps
    path('billing/', include('alexia.apps.billing.urls')),
    path('consumption/', include('alexia.apps.consumption.urls')),
    path('organization/', include('alexia.apps.organization.urls')),
    path('profile/', include('alexia.apps.profile.urls')),
    path('scheduling/', include('alexia.apps.scheduling.urls')),
    path('ical', scheduling_views.ical),
    path('ical/<str:ical_id>', scheduling_views.personal_ical, name='ical'),

    path('api/', include('alexia.api.urls')),

    # "Static" general_views
    path('healthz/', general_views.healthz_view, name='healthz_simple'),
    path('about/', general_views.AboutView.as_view(), name='about'),
    path('help/', general_views.HelpView.as_view(), name='help'),
    path('login_complete/', general_views.login_complete, name='login_complete'),
    path('legacy_login/', general_views.login, name='login'),
    path('legacy_logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', general_views.RegisterView.as_view(), name='register'),
    path('change_current_organization/<str:slug>/',
        general_views.ChangeCurrentOrganizationView.as_view(), name='change-current-organization'),
    path('oidc/', include('mozilla_django_oidc.urls')),

    # Django Admin
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),

    # Internationalization
    path('i18n/', include('django.conf.urls.i18n')),

    # Robots
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

# Debug toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    # Translation application for development
    urlpatterns += [
        path('translations/', include('rosetta.urls'), name='translations')
    ]
    # Static and media files in development mode
    urlpatterns += [
        re_path(r'^%s(?P<path>.*)$' % (settings.MEDIA_URL[1:]), serve, {'document_root': settings.MEDIA_ROOT},
                name='media'),
        re_path(r'^%s(?P<path>.*)$' % (settings.STATIC_URL[1:]), serve, {'document_root': settings.STATIC_ROOT},
                name='static'),
    ]
