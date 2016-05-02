from django.conf.urls import include, url
from django.contrib import admin

from profiles.views import landing

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', landing, name='landing'),
    url(r'^profile/', include('profiles.urls')),
    url(r'^bets/', include('bets.urls')),
]
