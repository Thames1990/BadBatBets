import logging

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect

from .forms import SignupForm, LoginForm, FeedbackForm
from .models import Feedback
from bets.util import generate_profile_resolved_bet
from profiles.util import user_authenticated

logger = logging.getLogger(__name__)


@login_required
def profile(request):
    resolved_bets = generate_profile_resolved_bet(request.user.profile)
    return render(request, 'profiles/profile.html', {
        'resolved_placed_choice_bets': resolved_bets['resolved_placed_choice_bets'],
        'resolved_placed_date_bets': resolved_bets['resolved_placed_date_bets'],
        'feedback': Feedback.objects.all()
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


def general_terms_and_conditions_view(request):
    if user_authenticated(request.user) or request.user.is_authenticated():
        return render(request, 'profiles/general_terms_and_conditions.html')
    else:
        return render(request, 'profiles/general_terms_and_conditions_anonymous.html')


def privacy_policy_view(request):
    if user_authenticated(request.user) or request.user.is_authenticated():
        return render(request, 'profiles/privacy_policy.html')
    else:
        return render(request, 'profiles/privacy_policy_anonymous.html')


@login_required
def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, "Thank you for your valuable feedback. We will use it to make BBB even better.")
            return redirect('profiles:profile')
    else:
        form = FeedbackForm()

    return render(request, 'profiles/feedback.html', {'form': form})


def resolve_feedback(request, id):
    try:
        feedback = Feedback.objects.get(id=id)
        feedback.resolved = True
        feedback.save()
    except Feedback.DoesNotExist:
        messages.info(request, "Feedback does not exist")
        raise Http404
    return HttpResponseRedirect(reverse('profiles:profile'))
