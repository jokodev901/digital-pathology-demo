from django.test import TestCase, Client
from django.urls import reverse

from authentication.models import User


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client(HTTP_X_FORWARDED_PROTO='https')
        self.username = 'authpageuser'
        self.password = 'password123'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_template(self):
        url = reverse('login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')


    def test_successful_login(self):
        """Verify valid credentials log the user in and redirect."""
        url = reverse('login')
        data = {'username': self.username, 'password': self.password}

        response = self.client.post(url, data=data, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)

    def test_invalid_login(self):
        """Verify wrong credentials keep user on login page with errors."""
        url = reverse('login')
        data = {'username': self.username, 'password': 'wrongpassword'}

        response = self.client.post(url, data=data, follow=True)

        # Should stay on page (200) but not be authenticated
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)
        # Check if error message is present in the context
        self.assertTrue(response.context['form'].errors)