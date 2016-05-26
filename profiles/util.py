def user_authenticated(user):
    return \
        user.is_authenticated() and \
        user.profile.verified and \
        user.profile.accepted_agb and \
        user.profile.accepted_privacy_policy
