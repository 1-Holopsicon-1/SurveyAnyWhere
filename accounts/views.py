import datetime
import json
from random import randint

import pytz
from django.contrib import messages, admin
from django.contrib.admin import AdminSite
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.template.defaulttags import url
from django.urls import reverse, include
from django.utils import timezone
from django.views.generic import RedirectView

from accounts.decorators import staff_required, ban_check
from accounts.emailing import get_confirm_email_body, get_password_email_body
from accounts.forms import RegistrationForm, PasswordResetForm
from accounts.models import UserProperties, Complaint
from surveyanywhere.settings import EMAIL_HOST_USER

#<editor-fold desc="MAIN PART">
from surveys.models import Survey, SurveyQuestion, SurveyAnswer
from surveys.views import check_string


def register(request):
    if request.user.is_authenticated:
        return redirect(reverse('main'))

    form = RegistrationForm()

    if request.method == 'POST':
        form = RegistrationForm(request)
        if form.is_valid():
            form.save()
            username = form.data.get('username')
            userParams = UserProperties(user=User.objects.get(username=username))
            userParams.save()
            messages.info(request, f'Account with username {username} created.')
            return redirect(reverse('user_login'))

    context = {}
    return render(request, 'signup.html', context)

@login_required(login_url='user_login')
@ban_check(redirect_html='permissionError.html', parameters_permanent={'code': 3}, parameters_temporary={'code': 2})
def sendEmail(request):
    user = request.user
    userProp = UserProperties.objects.get(user=user)
    number = randint(100000, 999999)
    email = EmailMessage(
        'Account email verification',
        get_confirm_email_body(user.username, number),
        EMAIL_HOST_USER,
        [user.email],
    )
    email.send()
    userProp.email_key_verification = number
    userProp.email_confirm_called = timezone.now()
    userProp.save()
    return redirect(reverse('user_register_confirm'))

@login_required(login_url='user_login')
@ban_check(redirect_html='permissionError.html', parameters_permanent={'code': 3}, parameters_temporary={'code': 2})
def registerConfirm(request):
    user = request.user

    userProp = UserProperties.objects.get(user=user)
    value = userProp.email_key_verification
    if value == 0 or (timezone.now() - userProp.password_restore_called).total_seconds() > 1800:
        userProp.email_key_restoration = 0
        userProp.save()
        return redirect(reverse('main'))

    if request.method == "POST":
        digit = request.POST.get('Digit1')
        digit += request.POST.get('Digit2')
        digit += request.POST.get('Digit3')
        digit += request.POST.get('Digit4')
        digit += request.POST.get('Digit5')
        digit += request.POST.get('Digit6')

        if int(digit) == value:
            userProp.email_key_verification = 0
            userProp.email_verified = True
            userProp.save()
            messages.info(request, f'Email of {user.username} verified.')
            return redirect(reverse('user_login'))
        else:
            messages.error(request, f'Email code incorrect.')
    context = {
        'key': value,
    }
    return render(request, 'signup_confirm.html', context)

def authentication(request):
    '''if not acception(request):
        return redirect(reverse('user_register'))    ?????? ?? ???????????????? ?????????????????????????????????? ??????????????'''

    if request.user.is_authenticated:
        return redirect(reverse('main'))

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('main'))
        else:
            messages.info(request, 'Username or password incorrect')

    context = {}
    return render(request, 'signin.html', context)

def deauthentication(request):
    logout(request)
    return redirect(reverse('user_login'))
#</editor-fold>

def restore_access(request):
    if request.user.is_authenticated:
        return redirect(reverse('main'))

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')

        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            user = None

        if user is not None and user.email == email:
            number = randint(100000, 999999)
            email = EmailMessage(
                'Account access restoration',
                get_password_email_body(username, number),
                EMAIL_HOST_USER,
                [email],
            )
            email.send()
            userParams = UserProperties.objects.get(user=user)
            userParams.email_key_restoration = number
            userParams.password_restore_called = timezone.now()
            userParams.save()
            return redirect(reverse('user_restore_confirm') + f'?user={username}')
        else:
            messages.info(request, 'Username or email incorrect')

    context = {}
    return render(request, 'restore.html', context)

def restore_access_check(request):
    if request.user.is_authenticated:
        return redirect(reverse('main'))

    username = request.GET.get('user', '')
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return redirect(reverse('main'))

    userProp = UserProperties.objects.get(user=user)
    value = userProp.email_key_restoration
    if value == 0 or (timezone.now() - userProp.password_restore_called).total_seconds() > 1800:
        userProp.email_key_restoration = 0
        userProp.save()
        return redirect(reverse('main'))

    if request.method == "POST":
        digit = request.POST.get('Digit1')
        digit += request.POST.get('Digit2')
        digit += request.POST.get('Digit3')
        digit += request.POST.get('Digit4')
        digit += request.POST.get('Digit5')
        digit += request.POST.get('Digit6')

        if int(digit) == value:
            return redirect(reverse('user_restore_main') + f'?user={username}')
        else:
            messages.error(request, f'Email code incorrect.')
    context = {
        'key': value,
    }
    return render(request, 'restore_check.html', context)

def restore_access_main(request):
    if request.user.is_authenticated:
        return redirect(reverse('main'))

    username = request.GET.get('user', None)
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return redirect(reverse('main'))
    userProp = UserProperties.objects.get(user=user)
    if userProp.email_key_restoration == 0 or (timezone.now() - userProp.password_restore_called).total_seconds() > 1800:
        userProp.email_key_restoration = 0
        userProp.save()
        return redirect(reverse('main'))

    context = {}
    form = SetPasswordForm(user)
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            new_password = request.POST['new_password1']
            if not check_password(new_password, user.password):
                user.set_password(new_password)
                user.save()
                userProp.email_key_restoration = 0
                userProp.save()
                messages.info(request, 'Password was updated')
                return HttpResponseRedirect(reverse('user_login'))
            else:
                messages.error(request, 'New password is the same as the old one')
    context['form'] = form
    return render(request, 'restore_main.html', context)

@login_required(login_url='user_login')
@ban_check(redirect_html='permissionError.html', parameters_permanent={'code': 3}, parameters_temporary={'code': 2})
def changePassword(request):
    user = request.user
    context = {}
    form = PasswordChangeForm(user)
    if request.method == 'POST':
        form = PasswordResetForm(request)
        if form.is_valid():
            form.save()
            logout(request)
            messages.info(request, 'Password was updated')
            return HttpResponseRedirect(reverse('user_login'))
    context['form'] = form

    return render(request, 'password_reset.html', context)

@ban_check(redirect_html='permissionError.html', parameters_permanent={'code': 3}, parameters_temporary={'code': 2})
def userInfo(request):
    username = request.GET.get('user', None)
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return redirect(reverse('main'))

    context = {
        'isOwner': False,
        'username': username,
        'userProperties': None,
    }
    if request.user.is_authenticated and request.user.username == username:
        context['isOwner'] = True
        context['userProperties'] = UserProperties.objects.get(user=user)
        surveys = Survey.objects.filter(creator=user).order_by('-rating', '-creationTime', 'title')
        context['surveys'] = []
        for survey in surveys:
            participants = set()
            for question in SurveyQuestion.objects.filter(survey=survey):
                for answer in SurveyAnswer.objects.filter(surveyQuestion=question):
                    for user in answer.users.all():
                        participants.add(user)
            context['surveys'].append([survey, len(participants)])
    return render(request, 'user_page.html', context)

@login_required(login_url='user_login')
@ban_check(redirect_html='permissionError.html', parameters_permanent={'code': 3}, parameters_temporary={'code': 2})
@staff_required(redirect_html='permissionError.html', parameters={'code': 0})
def complaint_check(request):
    context = {}
    complaints = Complaint.objects.all().order_by('date', 'title')
    context['complaints'] = complaints
    return render(request, 'complaints.html', context)

@login_required(login_url='user_login')
@ban_check(redirect_html='permissionError.html', parameters_permanent={'code': 3}, parameters_temporary={'code': 2})
@staff_required(redirect_html='permissionError.html', parameters={'code': 0})
def complaintInfo(request):
    complaintID = request.GET.get('id', None)
    try:
        complaint = Complaint.objects.get(id=complaintID)
    except:
        return redirect(reverse('main'))

    if request.is_ajax():
        if request.POST.get('reject', None) is not None:
            pass
        else:
            verdict = request.POST.get('verdict')
            userProp = UserProperties.objects.get(user=complaint.user)
            if verdict == "Permanent ban":
                userProp.permanent_ban = True
                userProp.save()
            elif verdict == "Temporary right limit":
                switch = request.POST.get('switch-input')
                if switch == 'true':
                    until_time = request.POST.get('until-time')
                    until_time = until_time.split('-')
                    userProp.access_limited = timezone.get_current_timezone().normalize(datetime.datetime(int(until_time[0]), int(until_time[1]), int(until_time[2]), tzinfo=pytz.UTC))
                else:
                    for_time = request.POST.get('for-time')
                    for_time = for_time.split()
                    number = int(for_time[0])
                    if 'minute' in for_time[1]:
                        userProp.access_limited = timezone.now() + timezone.timedelta(minutes=number)
                    elif 'hour' in for_time[1]:
                        userProp.access_limited = timezone.now() + timezone.timedelta(hours=number)
                    elif 'day' in for_time[1]:
                        userProp.access_limited = timezone.now() + timezone.timedelta(days=number)
                userProp.save()
            elif verdict == "Temporary ban":
                switch = request.POST.get('switch-input')
                if switch == 'true':
                    until_time = request.POST.get('until-time')
                    until_time = until_time.split('-')
                    userProp.banned = timezone.get_current_timezone().normalize(datetime.datetime(int(until_time[0]), int(until_time[1]), int(until_time[2]), tzinfo=pytz.UTC))
                else:
                    for_time = request.POST.get('for-time')
                    for_time = for_time.split()
                    number = int(for_time[0])
                    if 'minute' in for_time[1]:
                        userProp.banned = timezone.now() + timezone.timedelta(minutes=number)
                    elif 'hour' in for_time[1]:
                        userProp.banned = timezone.now() + timezone.timedelta(hours=number)
                    elif 'day' in for_time[1]:
                        userProp.banned = timezone.now() + timezone.timedelta(days=number)
                userProp.save()
        complaint.delete()


    context = {'complaint': complaint}
    return render(request, 'complaint_watch.html', context)

@login_required(login_url='user_login')
def createComplaint(request):
    user = request.GET.get('user', None)
    if user == None:
        return redirect(reverse('main'))

    if request.is_ajax():
        title = request.POST.get('title')
        description = request.POST.get('description')
        if not check_string(title):
            messages.error(request, 'Wrong title')
        if not check_string(description):
            messages.error(request, 'Wrong description')

        if len(messages.get_messages(request)) == 0:
            messages.success(request, 'Check succeeded')

            complaint = Complaint(user=User.objects.get(username=user), author=request.user, title=title, description=description)
            complaint.save()

            response = HttpResponseRedirect(reverse('main'))
            response.status_code = 278
            return response

        data = {}

        # <editor-fold desc="SEND-MESSAGES">
        sended_messages = []
        for message in messages.get_messages(request):
            sended_messages.append({
                "level": message.level,
                "message": message.message,
                "extra_tags": message.tags,
            })
        data['messages'] = sended_messages
        # </editor-fold>

        return HttpResponse(json.dumps(data), content_type="application/json")

    context = {
        'user': user,
    }
    return render(request, 'complaint_create.html', context)

