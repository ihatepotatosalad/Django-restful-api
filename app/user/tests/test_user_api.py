from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')

TOKEN_URL = reverse('user:token')

ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        payload = {
            'email': 'test@example.com',
            'password': 'scoretestpassword',
            'name': 'test'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        payload = {
            'email': 'test@example.com',
            'password': 'scoretestpassword',
            'name': 'test'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        payload = {
            'email': 'test4@example.com',
            'password': 'test'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        test_user = {
            'email': 'test@example.com',
            'name': 'test',
            'password': 'scoretestpassword'
        }
        create_user(**test_user)

        payload = {
            'email': test_user['email'],
            'password': test_user['password']
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_request(self):
        test_user = {
            'email': 'test@example.com',
            'name': 'test',
            'password': 'scoretestpassword'
        }
        create_user(**test_user)

        payload = {
            'email': test_user['email'],
            'password': 'badpassword'
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_user_no_password(self):
        test_user = {
            'email': 'test@example.com',
            'name': 'test',
            'password': 'scoretestpassword'
        }
        payload = {
            'email': test_user['email'],
            'password': ''
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITest(TestCase):
    def setUp(self):

        test_user = {
            'email': 'test@example.com',
            'password': 'scoretestpassword',
            'name': 'test'
        }
        self.user = create_user(**test_user)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_user_post_fail(self):
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_update_profile(self):
        payload = {
            'name': 'new_name',
            'password': 'new_password'
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])

        self.assertTrue(self.user.check_password(payload['password']))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
