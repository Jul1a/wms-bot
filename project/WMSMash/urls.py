from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.auth.views import login, logout

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^WMSMash/', include('WMSMash.foo.urls')),
    (r'^accounts/login/$', 'WMSMash.tree.views.login'),
    (r'^templates/accounts/login/$', 'WMSMash.tree.views.login'),
    (r'^accounts/logout/$', 'WMSMash.tree.views.logout_view'),
    (r'^templates/accounts/logout/$', 'WMSMash.tree.views.logout_view'),
    (r'^accounts/register/$', 'WMSMash.tree.views.register'),
    (r'^templates/accounts/register/$', 'WMSMash.tree.views.register'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^templates/(?P<path>.*)$', 'django.views.static.serve', 
      {'document_root':settings.MEDIA_ROOT}
    ),
    # Uncomment the next line to enable the admin:
    #(r'^admin/', include(admin.site.urls)),
    (r'^$', 'WMSMash.tree.views.show_page'),
)
