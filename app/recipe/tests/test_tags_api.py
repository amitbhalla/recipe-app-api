from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

TAGS_URL = reverse("recipe:tag-list")


class PublicTagsApiTests(TestCase):
    """Tests the publically available Tag API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retriving tag info"""
        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test autheticated API responses"""

    def setUp(self):
        payload = {
            "email": "test@mail.com",
            "password": "password123",
        }
        self.user = get_user_model().objects.create_user(**payload)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_tags(self):
        """Test retriving tags when logged in"""
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")
        response = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that User only sees their tags"""
        # Create a new user apart from one from setUp
        # Give them a TAG
        # Ensure that tag does not show up in response
        payload = {
            "email": "user2@mail.com",
            "password": "password123",
        }
        user2 = get_user_model().objects.create_user(**payload)
        # Assign to new user
        Tag.objects.create(user=user2, name="Fruity")

        # Assign to original user
        tag = Tag.objects.create(user=self.user, name="Comfort Food")

        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {
            "name": "Test Tag",
        }
        self.client.post(TAGS_URL, payload)
        exists = Tag.objects.filter(
            user=self.user, name=payload["name"]
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Creating a new tag with invalid payload"""
        payload = {
            "name": "",
        }
        response = self.client.post(TAGS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """Test filtering tags by those assigned to recipes"""
        tag1 = Tag.objects.create(user=self.user, name="Breakfast")
        tag2 = Tag.objects.create(user=self.user, name="Lunch")
        recipe = Recipe.objects.create(
            title="Coriander eggs on toast",
            time_minutes=10,
            price=5.00,
            user=self.user,
        )
        recipe.tags.add(tag1)
        response = self.client.get(TAGS_URL, {"assigned_only": 1})
        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_retrieve_tags_assigned_unique(self):
        """Test filtering tags by assigned returns unique items"""
        tag = Tag.objects.create(user=self.user, name="Breakfast")
        Tag.objects.create(user=self.user, name="Lunch")
        recipe1 = Recipe.objects.create(
            title="Pancakes", time_minutes=5, price=3.00, user=self.user
        )
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            title="Porridge", time_minutes=3, price=2.00, user=self.user
        )
        recipe2.tags.add(tag)
        response = self.client.get(TAGS_URL, {"assigned_only": 1})

        self.assertEqual(len(response.data), 1)
