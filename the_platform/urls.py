from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.decorators import permission_required
from django.views.generic import TemplateView

from bets.views import index_view
from profiles.views import login_user, signup, feedback

from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # Index page
    url(r'^$', index_view, name='index'),

    # When the user goes to /login
    url(r'^login/', login_user),

    # When the user goes to /signup
    url(r'^signup/$', signup),

    # When the user goes to /feedback
    url(r'feedback/$', feedback),

    # Profiles sub-module
    url(r'^profile/', include('profiles.urls')),

    # Bets sub-module
    url(r'^bets/', include('bets.urls')),

    # Log view.
    url(
        r'^log/$',
        permission_required('admin')
        (TemplateView.as_view(template_name='the_platform/bbb.log', content_type='text/plain')),
        name='log'
    )
]

handler403 = views.error403
handler404 = views.error404
handler500 = views.error500
