from django.conf.urls import url

from . import views

app_name = 'profiles'
urlpatterns = [
    url(r'^$', views.profile, name='profile'),
    url(r'^login/$', views.login_page, name='login'),
    url(r'^login/login/$', views.login_user, name='login_post')
]
