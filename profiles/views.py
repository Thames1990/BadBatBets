import logging

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect

from .forms import SignupForm, LoginForm, PaymentForm, FeedbackForm
from bets.util import generate_profile_resolved_bet
from profiles.util import user_authenticated

logger = logging.getLogger(__name__)


@login_required
def profile(request):
    resolved_bets = generate_profile_resolved_bet(request.user.profile)
    return render(request, 'profiles/profile.html', {
        'resolved_placed_choice_bets': resolved_bets['resolved_placed_choice_bets'],
        'resolved_placed_date_bets': resolved_bets['resolved_placed_date_bets'],
    })


def login_user(request):
    if user_authenticated(request.user):
        return redirect('index')
    else:
        if request.method == 'POST':
            form = LoginForm(data=request.POST)
            if form.is_valid():
                login(request, form.get_user())
                return redirect('profiles:profile')
        else:
            form = LoginForm()

        return render(request, 'profiles/login.html', {'form': form})


@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "Logout successful")
    return redirect('profiles:login')


def signup(request):
    if user_authenticated(request.user):
        return redirect('index')
    else:
        if request.method == 'POST':
            form = SignupForm(request.POST)
            if form.is_valid():
                user = form.save()
                user.profile.accepted_general_terms_and_conditions = True
                user.profile.accepted_privacy_policy = True
                user.profile.save()
                return redirect(login_user)
        else:
            form = SignupForm()

        return render(request, 'profiles/signup.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(login_user)

    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'profiles/change_password.html', {'form': form})


@login_required
def payment(request):
    if user_authenticated(request.user) and request.user.is_superuser:
        if request.method == 'POST':
            form = PaymentForm(request.POST)
            if form.is_valid():
                form.save(authorised=request.user)
        else:
            form = PaymentForm()

        return render(request, 'profiles/payment.html', {'form': form})
    else:
        messages.info(request, "You're not authenticated. Please get in contact with an administrator.")
        if not request.user.is_anonymous():
            logger.warning("Unverified user " + request.user.username + " tried to view payment page.")
            return redirect('profiles:profile')
        raise PermissionDenied


def general_terms_and_conditions_view(request):
    return render(request, 'profiles/general_terms_and_conditions.html')


def privacy_policy_view(request):
    return render(request, 'profiles/privacy_policy.html')


@login_required
def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            # TODO: Redirect to somewhere useful...
    else:
        form = FeedbackForm()

    return render(request, 'profiles/feedback.html', {'form': form})
