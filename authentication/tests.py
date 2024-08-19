from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
import json

class ValidationTests(TestCase):
    
    def setUp(self):
        # Create a user for testing purposes
        self.username = 'testuser'
        self.email = 'testuser@example.com'
        self.password = 'password123'
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )

    def test_valid_email(self):
        # Test valid email
        response = self.client.post(reverse('validate-email'), 
                                   json.dumps({'email': 'newuser@example.com'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertNotIn('email_error', data)
        
    def test_invalid_email(self):
        # Test invalid email
        response = self.client.post(reverse('validate-email'), 
                                   json.dumps({'email': 'invalid-email'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('email_error', data)

    def test_valid_username(self):
        # Test valid username
        response = self.client.post(reverse('validate-username'), 
                                   json.dumps({'username': 'newusername'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertNotIn('username_error', data)
        
    def test_invalid_username(self):
        # Test invalid username (already taken)
        response = self.client.post(reverse('validate-username'), 
                                   json.dumps({'username': self.username}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.content)
        self.assertIn('username_error', data)
