from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):
    def setUp(self):
        self.client = Client()
        admin_user = get_user_model().objects.create_superuser(
            'admin@example.com', 'scoretestpassword')

        self.client.force_login(admin_user)
        self.user = get_user_model().objects.create_user(
            email='exampleuser@example.com',
            password='testing',
            name='Test User'
        )

    def test_user_list(self):
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        url = reverse('admin:core_user_add')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
