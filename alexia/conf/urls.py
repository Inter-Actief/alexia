from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

from alexia.apps.billing.views import JulianaView
from alexia.apps.consumption.views import complete_dcf, dcf
from alexia.apps.general import views as general_views
from alexia.apps.scheduling import views as scheduling_views

urlpatterns = [
    # Root
    path('', RedirectView.as_view(pattern_name='event-list', permanent=True)),

    # Short urls to 'subsystems'
    path('dcf/<int:pk>/', include([
        path('', dcf, name='dcf'),
        path('check/', complete_dcf, name='dcf-complete'),
    ])),
    path('ical/', include([
        path('', scheduling_views.ical),
        path('<ical_id>/', scheduling_views.personal_ical, name='ical'),
    ])),
    path('juliana/<int:pk>/', JulianaView.as_view(), name='juliana'),

    # Apps
    path('api/', include('alexia.api.urls')),
    path('billing/', include('alexia.apps.billing.urls')),
    path('consumption/', include('alexia.apps.consumption.urls')),
    path('organization/', include('alexia.apps.organization.urls')),
    path('profile/', include('alexia.apps.profile.urls')),
    path('scheduling/', include('alexia.apps.scheduling.urls')),

    # "Static" general_views
    path('about/', general_views.AboutView.as_view(), name='about'),
    path('help/', general_views.HelpView.as_view(), name='help'),
    path('login/', general_views.login, name='login'),
    path('logout/', auth_views.logout, name='logout'),
    path('register/', general_views.RegisterView.as_view(), name='register'),
    path('change_current_organization/<slug:slug>/',
         general_views.ChangeCurrentOrganizationView.as_view(), name='change-current-organization'),

    # Django Admin
    path('admin/', include([
        path('', admin.site.urls),
        path('doc/', include('django.contrib.admindocs.urls')),
    ])),

    # Internationalization
    path('i18n/', include('django.conf.urls.i18n')),

    # Robots
    path('robots\.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

# Debug toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
