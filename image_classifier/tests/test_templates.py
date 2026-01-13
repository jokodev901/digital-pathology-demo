import io
from PIL import Image

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from authentication.models import User


class PLIPTemplateTests(TestCase):
    def generate_test_image(self):
        file = io.BytesIO()
        image = Image.new('RGB', (100, 100), 'white')
        image.save(file, 'jpeg')
        file.seek(0)
        return SimpleUploadedFile('image.jpg', file.read(), content_type='image/jpeg')

    def setUp(self):
        self.client = Client(HTTP_X_FORWARDED_PROTO='https')
        self.user = User.objects.create_user(username='plippageuser', password='password123')
        self.contrib_user = User.objects.create_user(username='plipcontribuser', password='password123',
                                                     is_contributor=True)
        self.test_image = self.generate_test_image()

    def test_template_plip(self):
        url = reverse('plip')
        self.client.force_login(self.contrib_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'plip.html')
        self.assertContains(response, 'name="image"')
        self.assertContains(response, 'name="labels"')
        self.assertContains(response, 'name="expected_label"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')

    def test_template_plip_form(self):
        url = reverse('plip')
        self.client.force_login(self.contrib_user)

        data = {
            'labels': "test, labels",
            'image': self.test_image,
            'expected_label': "test"
        }

        response = self.client.post(url, data, format='multipart')
        self.assertContains(response, 'alt="Uploaded Image"')

    def test_contrib_template_plip(self):
        # user without is_contributor should fail
        url = reverse('plip')
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_contrib_template_plip_form(self):
        # user without is_contributor should fail
        url = reverse('plip')
        self.client.force_login(self.user)

        data = {
            'labels': "test, labels",
            'image': self.test_image,
            'expected_label': "test"
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 403)

    def test_template_plip_data_browser(self):
        url = reverse('plip_data')
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'plip_data_browser.html')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, 'name="label_0"')
        self.assertContains(response, '<th>Image</th>')
