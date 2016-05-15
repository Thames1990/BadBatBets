from django.conf.urls import url

from . import views

app_name = 'bets'
urlpatterns = [
    url(r'^create/choice/$', views.create_choice_bet, name="create_choice"),
]
