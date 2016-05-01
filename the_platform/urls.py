from django.conf.urls import include, url
from django.contrib import admin

from profiles.views import landing

urlpatterns = [
    url(r'^bets/', include('bets.urls')),
    url(r'^admin/', admin.site.urls),
    # Profiles sub-module
    url(r'^profile/', include('profiles.urls')),
    # Landing page
    url(r'^$', landing, name='landing')
]
