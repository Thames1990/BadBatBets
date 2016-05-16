from django.conf.urls import url

from . import views

app_name = 'bets'
urlpatterns = [
    url(r'^create/date/$', views.create_choice_bet, name="create_choice"),
]
