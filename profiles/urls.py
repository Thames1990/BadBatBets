from django.conf.urls import url

from . import views

app_name = 'profiles'
urlpatterns = [
    url(r'^$', views.profile, name='profile'),
    url(r'login/$', views.login, name='login'),
]
