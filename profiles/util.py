from django.contrib.auth.models import User, AnonymousUser


def user_authenticated(user):
    """
    Checks if a user is authenticated.
    :param user: User to check
    :return: True, if the useris verified and accepted general terms and conditions as well as the privacy policy;
    False otherwise.
    """
    if isinstance(user, User):
        return \
            user.is_authenticated and \
            user.profile.verified and \
            user.profile.accepted_general_terms_and_conditions and \
            user.profile.accepted_privacy_policy
    elif isinstance(user, AnonymousUser):
        return False
    else:
        pass
