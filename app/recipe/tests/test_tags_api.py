from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from core.models import Tag

from recipe.serializers import TagSerializer


TAG_URL = reverse('recipe:tag-list')


def create_tag_url(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='test@example.com', password='testing123'):
    return get_user_model().objects.create_user(email, password)


class PublicTagsAPIRequest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPIRequest(TestCase):

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_fetch_tags(self):
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Desert')
        tags = Tag.objects.all().order_by('-name')
        res = self.client.get(TAG_URL)
        serializar = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializar.data)

    def test_user_limited_results(self):
        user2 = create_user(email='test2@example.com', password='testing')
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=user2, name='Desert')
        res = self.client.get(TAG_URL)
        self.assertEqual(len(res.data), 1)

    def test_update_tag(self):
        tag = Tag.objects.create(user=self.user, name='Vegan')
        payload = {
            'name': 'Desert'
        }
        self.client.patch(create_tag_url(tag.id), payload)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])
