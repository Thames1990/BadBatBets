from django.conf.urls import url

from . import views

app_name = 'profiles'
urlpatterns = [
    url(r'^$', views.profile, name='profile'),

    # Login mechanism
    url(r'^login/$', views.login_user, name='login'),
    url(r'^logout/$', views.logout_user, name='logout'),

    # Signup mechanism
    url(r'^signup/$', views.signup, name='signup'),
]
