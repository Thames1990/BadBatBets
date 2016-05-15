from django.conf.urls import url, include
from django.contrib import admin

from profiles.views import landing, login_user, signup

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # When the user goes to /login
    url(r'^login/', login_user),

    # When the user goes to /signup
    url(r'^signup/$', signup),

    # Profiles sub-module
    url(r'^profile/', include('profiles.urls')),

    # Landing page
    url(r'^$', landing, name='landing'),

    # TODO change this to landing
    url(r'^bets/', include('bets.urls')),
]
