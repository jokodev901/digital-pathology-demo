import io
from PIL import Image

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework import status

from authentication.models import User


class PLIPApiTests(APITestCase):
    def generate_test_image(self):
        file = io.BytesIO()
        image = Image.new('RGB', (100, 100), 'white')
        image.save(file, 'jpeg')
        file.seek(0)
        return SimpleUploadedFile('image.jpg', file.read(), content_type='image/jpeg')


    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='password123')
        self.token = Token.objects.create(user=self.user)
        self.test_image = self.generate_test_image()


    def test_pliplist_session(self):
        self.client.force_login(user=self.user)
        url = reverse('plip-list')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_pliplist_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('plip-list')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_plipinput_session(self):
        self.client.force_login(user=self.user)
        url = reverse('plip-input')

        data = {
            'labels': "test, labels",
            'image': self.test_image,
            'expected_label': "test"
        }

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('filename', response.json())


    def test_plipinput_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('plip-input')

        data = {
            'labels': "test, labels",
            'image': self.test_image,
            'expected_label': "test"
        }

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('filename', response.json())