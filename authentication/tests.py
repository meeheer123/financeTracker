from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import json
from userpreferences.models import UserPreference

class AuthenticationTests(TestCase):
    
    def setUp(self):
        self.username = 'testuser'
        self.email = 'testuser@example.com'
        self.password = 'password123'
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )
        UserPreference.objects.create(user=self.user, currency='INR')
    
    def test_email_validation_valid(self):
        response = self.client.post(reverse('validate-email'), 
                                   json.dumps({'email': 'newuser@example.com'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertNotIn('email_error', data)

    def test_email_validation_invalid(self):
        response = self.client.post(reverse('validate-email'), 
                                   json.dumps({'email': 'invalid-email'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('email_error', data)

    def test_email_validation_taken(self):
        response = self.client.post(reverse('validate-email'), 
                                   json.dumps({'email': self.email}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.content)
        self.assertIn('email_error', data)

    def test_username_validation_valid(self):
        response = self.client.post(reverse('validate-username'), 
                                   json.dumps({'username': 'newusername'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertNotIn('username_error', data)

    def test_username_validation_invalid(self):
        response = self.client.post(reverse('validate-username'), 
                                   json.dumps({'username': 'testuser'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.content)
        self.assertIn('username_error', data)

    def test_username_validation_taken(self):
        response = self.client.post(reverse('validate-username'), 
                                json.dumps({'username': self.username}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.content)
        self.assertIn('username_error', data)

    def test_registration_valid(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        })
        self.assertRedirects(response, reverse('login'))

    def test_registration_short_password(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'short'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/register.html')
        self.assertContains(response, 'Password too short')

    def test_verification_view(self):
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(self.user)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        response = self.client.get(reverse('activate', kwargs={'uidb64': uidb64, 'token': token}))
        self.assertRedirects(response, reverse('login'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_verification_view_invalid_token(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        response = self.client.get(reverse('activate', kwargs={'uidb64': uidb64, 'token': 'invalid-token'}))
        self.assertRedirects(response, reverse('login'))

    def test_login_valid(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        })
        self.assertRedirects(response, reverse('expenses'))

    def test_login_invalid(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid credentials, try again')

    def test_logout(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_request_password_reset_email(self):
        response = self.client.post(reverse('request-password'), {
            'email': self.email
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/reset-password.html')
    def test_complete_password_reset_valid(self):
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(self.user)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        response = self.client.post(reverse('reset-user-password', kwargs={'uidb64': uidb64, 'token': token}), {
            'password': 'newpassword123',
            'password2': 'newpassword123'
        })
        self.assertRedirects(response, reverse('login'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_complete_password_reset_invalid(self):
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(self.user)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        response = self.client.post(reverse('reset-user-password', kwargs={'uidb64': uidb64, 'token': token}), {
            'password': 'short',
            'password2': 'short'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/set-new-password.html')
        self.assertContains(response, 'Password too short')
