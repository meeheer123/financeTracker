from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string
from .utils import account_activation_token
from django.urls import reverse
from django.contrib import auth
import json
from userpreferences.models import UserPreference
from django.core.validators import validate_email
from django.contrib.auth.tokens import PasswordResetTokenGenerator

import threading

# Create your views here.

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    
    def run(self):
        self.email.send(fail_silently=False)

def email_validation_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data['email']
        try:
            validate_email(email)
            if User.objects.filter(email=email).exists():
                return JsonResponse({'email_error': 'Sorry, email in use. Choose another one.'}, status=409)
            return JsonResponse({'email_valid': True})
        except:
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)
        

def username_validation_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'Username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'Sorry, username in use. Choose another one.'}, status=409)
        return JsonResponse({'username_valid': True})

def registration_view(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('expenses')
        return render(request, 'authentication/register.html')
    
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'Password too short')
                    return render(request, 'authentication/register.html', context)

                user = User.objects.create_user(username=username, email=email, password=password)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                email_body = {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }

                link = reverse('activate', kwargs={
                               'uidb64': email_body['uid'], 'token': email_body['token']})

                email_subject = 'Activate your account'

                activate_url = 'http://'+current_site.domain+link

                email = EmailMessage(
                    email_subject,
                    'Hi '+user.username + ', Please use the link below to activate your account \n'+activate_url,
                    'noreply@semycolon.com',
                    [email],
                )
                EmailThread(email).start()
                messages.success(request, 'Account successfully created')
                # add default currency preference
                UserPreference.objects.create(user=user, currency='USD')
                return redirect('login')

        return render(request, 'authentication/register.html')

def verification_view(request, uidb64, token):
    try:
        id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=id)

        if not account_activation_token.check_token(user, token):
            return redirect('login'+'?message='+'User already activated')

        if user.is_active:
            return redirect('login')
        user.is_active = True
        user.save()

        messages.success(request, 'Account activated successfully')
        return redirect('login')

    except Exception as ex:
        pass

    return redirect('login')

def login_view(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('expenses')
        return render(request, 'authentication/login.html')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = User.objects.filter(username=username)
            if user.exists():
                if user.first().is_active:
                    user = auth.authenticate(username=username, password=password)
                    if user:
                        auth.login(request, user)
                        messages.success(request, 'Welcome, ' +
                                         user.username+' you are now logged in')
                        return redirect('expenses')
                    messages.error(
                        request, 'Invalid credentials, try again')
                    return render(request, 'authentication/login.html')
                else:
                    messages.error(
                        request, 'Account is not activated, please check your email')
                    return render(request, 'authentication/login.html')
        else:
            messages.error(request, 'Please fill all fields')
            return render(request, 'authentication/login.html')

def logout_view(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')

def RequestPasswordResetEmail(request):
    if request.method == "GET":
        return render(request, 'authentication/reset-password.html')
    
    if request.method == "POST":

        email = request.POST['email'].strip()

        context = {
            'values': request.POST
        }
        try:
            validate_email(email)
            current_site = get_current_site(request)
            user = User.objects.filter(email=email)

            if user.exists():
                email_contents = {
                'user': user[0],
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0]),
            }

            link = reverse('reset-user-password', kwargs={
                            'uidb64': email_contents['uid'], 'token': email_contents['token']})

            email_subject = 'Password Reset Instructions'

            reset_url = 'http://'+current_site.domain+link

            email = EmailMessage(
                email_subject,
                'Hi there, Please use the link below to reset your password \n'+ reset_url,
                'noreply@semycolon.com',
                [email],
            )
            EmailThread(email).start()

            messages.success(request, 'We have sent you an email to reset your password')
            
            return render(request, 'authentication/reset-password.html')
        except Exception as identifier:
            messages.error(request, 'Please enter a valid email')
            return render(request, 'authentication/reset-password.html', context)
        
        


def completePasswordReset(request, uidb64, token):
    if request.method == "GET":
        context = {
            'uidb64': uidb64,
            'token': token
        }

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, 'Password reset link is invalid, please request a new one')
                return render(request, 'authentication/reset-password.html')

        except Exception as identifier:
            messages.info(request, 'Something went wrong, try again')
            return render(request, 'authentication/set-new-password.html', context)

        return render(request, 'authentication/set-new-password.html', context)
    if request.method == "POST":
        context = {
            'uidb64': uidb64,
            'token': token
        }

        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'authentication/set-new-password.html', context)

        if len(password) < 6:
            messages.error(request, 'Password too short')
            return render(request, 'authentication/set-new-password.html', context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            print(password)
            user.save()

            messages.success(request, 'Password reset successful, you can now login with your new password')
            return redirect('login')
        except Exception as identifier:
            messages.info(request, 'Something went wrong, try again')
            return render(request, 'authentication/set-new-password.html', context)

        