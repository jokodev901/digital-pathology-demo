from django.test import TestCase, Client
from django.urls import reverse

from authentication.models import User


class CoreTemplateTests(TestCase):
    def setUp(self):
        self.client = Client(HTTP_X_FORWARDED_PROTO='https')
        self.user = User.objects.create_user(username='corepageuser', password='password123')

    def test_home_template(self):
        url = reverse('home')
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertContains(response, 'Welcome corepageuser')

    def test_profile_template(self):
        url = reverse('profile')
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/profile.html')
        self.assertContains(response, 'User Profile: corepageuser')