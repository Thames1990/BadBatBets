"""the_platform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from profiles.views import landing, login_user, signup

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
    url(r'^bet/', include('bets.urls')),
]
