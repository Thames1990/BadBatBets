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

    # Logout mechanism
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

    # Deposit funds in account
    url(
        r'^payment/$',
        views.payment,
        name='payment'
    ),

    # General terms and conditions
    url(
        r'^general_terms_and_conditions/$',
        views.general_terms_and_conditions_view,
        name='general_terms_and_conditions'
    ),

    # Privacy policy
    url(
        r'^privacy_policy/$',
        views.privacy_policy_view,
        name='privacy_policy'
    ),

    # Provide feedback
    url(
        r'feedback/$',
        views.feedback,
        name='feedback'
    )
]
