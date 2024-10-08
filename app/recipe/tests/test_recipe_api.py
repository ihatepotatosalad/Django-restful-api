from decimal import Decimal

from django.contrib.auth import get_user_model

from django.test import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def create_recipe(user, **kwargs):
    default = {
        'user': user,
        'title': 'recipe_title',
        'description': 'recipe_description',
        'time_minutes': 5,
        'price': Decimal(5.25),
        'link': 'http://example.com'
    }
    default.update(**kwargs)
    recipe = Recipe.objects.create(**default)

    return recipe


def detail_url(id):
    return reverse('recipe:recipe-detail', args=[id])


class PublicRecipeAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@example.com', 'testpassword')
        self.client = APIClient()

        self.client.force_authenticate(self.user)

    def test_fetch_recipes(self):
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        other_user = get_user_model().objects.create_user(
            'new@example.com', 'testinggogogo')
        create_recipe(user=other_user)
        create_recipe(user=self.user)
        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_single_recipe_view(self):
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        payload = {
            'user': self.user,
            'title': 'recipe_title',
            'description': 'recipe_description',
            'time_minutes': 5,
            'price': Decimal(5.25),
            'link': 'http://example.com'
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_create_recipe_with_tag(self):
        payload = {
            'title': 'thai curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'thai'}, {'name': 'Dinner'}]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        recipe = recipes[0]
        self.assertEqual(recipes.count(), 1)
        self.assertEqual(recipe.tags.count(), 2)

    def test_create_recipe_with_existing_tags(self):
        tag = Tag.objects.create(user=self.user, name='thai')
        payload = {
            'title': 'thai curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'thai'}, {'name': 'Dinner'}]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        recipe = recipes[0]
        self.assertEqual(recipes.count(), 1)
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        recipe = create_recipe(user=self.user)
        payload = {
            'tags': [{
                'name': 'Thai'
            }]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Thai')
        self.assertIn(new_tag, recipe.tags.all())

    def test_reassign_tags_recipe(self):
        breakfast_tag = Tag.objects.create(user=self.user, name='breakfast')
        thai_tag = Tag.objects.create(user=self.user, name='Thai')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(breakfast_tag)
        payload = {
            'tags': [{'name': 'Thai'}]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(thai_tag, recipe.tags.all())
        self.assertNotIn(breakfast_tag, recipe.tags.all())
