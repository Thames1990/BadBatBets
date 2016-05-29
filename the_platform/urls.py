from django.conf.urls import url, include, handler404
from django.contrib import admin

from profiles.views import landing, login_user, signup

from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # Landing page
    url(r'^$', landing, name='landing'),

    # When the user goes to /login
    url(r'^login/', login_user),

    # When the user goes to /signup
    url(r'^signup/$', signup),

    # Profiles sub-module
    url(r'^profile/', include('profiles.urls')),

    # Bets sub-module
    url(r'^bets/', include('bets.urls')),
]

handler404 = views.error404
