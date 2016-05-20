from django.conf.urls import url

from . import views

app_name = 'profiles'
urlpatterns = [
    url(
        r'^$',
        views.profile,
        name='profile'
    ),

    # Login mechanism
    url(
        r'^login/$',
        views.login_user,
        name='login'
    ),
    url(
        r'^logout/$',
        views.logout_user,
        name='logout'
    ),

    # Signup mechanism
    url(
        r'^signup/$',
        views.signup,
        name='signup'
    ),

    # Change Password
    url(
        r'^change_password/$',
        views.change_password,
        name='change_password'
    ),

    # View transactions
    url(
        r'^transactions/$',
        views.transactions,
        name='transactions'
    ),

    # General terms and conditions, privacy policy
    url(
        r'^general_terms_and_conditions/$',
        views.general_terms_and_conditions_view,
        name='general_terms_and_conditions'
    ),
    url(
        r'^privacy_policy/$',
        views.privacy_policy_view,
        name='privacy_policy'
    )
]
