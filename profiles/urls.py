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

    # Change Password
    url(r'^change_password/$', views.change_password, name='change_password'),

    # View transactions
    url(r'^transactions/$', views.transactions, name='transactions'),

    # Deposit funds in account
    url(r'^payment/$', views.payment, name='payment'),
]
