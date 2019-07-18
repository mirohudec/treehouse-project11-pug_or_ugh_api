from django.test import TestCase

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.test import (
    APIRequestFactory, force_authenticate, APIClient)

from . import models
from . import serializers

# coverage run --source='.' manage.py test myapp


class ModelsTests(TestCase):
    def setUp(self):
        form = UserCreationForm(data={
            'id': 1,
            'username': 'crit',
            'password1': '123',
            'password2': '123'
        })
        form.save()
        self.user = User.objects.get(id=1)

    def test_UserPref_created(self):
        # if UserPref exist no exception is raised
        models.UserPref.objects.get(user=self.user)

    def test_DogModel_success(self):
        data = {
            'name': 'one',
            'image_filename': '1.jpg',
            'age': 20,
            'breed': 'Labrador',
            'gender': 'm',
            'size': 'm',

        }
        dog = models.Dog.objects.create(**data)
        dog.full_clean()
        self.assertEqual(dog.name, data['name'])

    def test_DogModel_fail(self):
        data = {
            'name': 'one',
            'image_filename': '1.jpg',
            'age': 20,
            'breed': 'Labrador',
            'gender': 'male',
            'size': 'm',

        }
        dog = models.Dog.objects.create(**data)
        with self.assertRaises(ValidationError):
            dog.full_clean()

    def test_UserPref_success(self):
        data = {
            'user': self.user,
            'gender': 'm',
            'size': 'm',
            'age': 'b,y'
        }
        user_pref = models.UserPref.objects.create(**data)
        user_pref.full_clean()
        self.assertEqual(user_pref.age, data['age'])
        self.assertNotIn('f', user_pref.gender)

    def test_UserPref_fail(self):
        data = {
            'user': self.user,
            'gender': 'small',
            'size': 'medium',
            'age': 'baby,young'
        }
        user_pref = models.UserPref.objects.create(**data)
        with self.assertRaises(ValidationError):
            user_pref.full_clean()

    def test_UserDog_success(self):
        dog = {
            'name': 'one',
            'image_filename': '1.jpg',
            'age': 20,
            'breed': 'Labrador',
            'gender': 'm',
            'size': 'm',

        }
        data = {
            'user': self.user,
            'dog': models.Dog.objects.create(**dog),
            'status': 'l'
        }
        user_dog = models.UserDog.objects.create(**data)
        user_dog.full_clean()
        self.assertEqual(user_dog.status, data['status'])

    def test_UserDog_fail(self):
        dog = {
            'name': 'one',
            'image_filename': '1.jpg',
            'age': 20,
            'breed': 'Labrador',
            'gender': 'm',
            'size': 'm',

        }
        data = {
            'user': self.user,
            'dog': models.Dog.objects.create(**dog),
            'status': 'liked'
        }
        user_dog = models.UserDog.objects.create(**data)
        with self.assertRaises(ValidationError):
            user_dog.full_clean()


class DogSerializerTests(TestCase):
    def setUp(self):
        self.dog_data = {
            'name': 'one',
            'image_filename': '1.jpg',
            'age': 20,
            'breed': 'Labrador',
            'gender': 'm',
            'size': 'm',
        }
        self.serializer_data = {
            'name': 'one',
            'image_filename': '1.jpg',
            'age': 20,
            'breed': 'Labrador',
            'gender': 'm',
            'size': 'm',
        }
        self.dog = models.Dog.objects.create(**self.dog_data)
        self.serializer = serializers.DogSerializer(instance=self.dog)

    def test_dog_expected_fields(self):
        data = self.serializer.data

        self.assertCountEqual(
            data.keys(), ['name', 'image_filename', 'age', 'breed',
                          'gender', 'size', 'id'])

    def test_name_field_success(self):
        data = self.serializer.data

        self.assertEqual(data['name'], self.dog_data['name'])

    def test_image_filename_field_succes(self):
        data = self.serializer.data

        self.assertEqual(data['image_filename'],
                         self.dog_data['image_filename'])

    def test_age_field_succes(self):
        self.serializer_data['age'] = -1

        serializer = serializers.DogSerializer(data=self.serializer_data)

        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors, ['age'])

    def test_age_field_fail(self):
        data = self.serializer.data

        self.assertEqual(data['age'], self.dog_data['age'])

    def test_breed_field_succes(self):
        data = self.serializer.data

        self.assertEqual(data['breed'], self.dog_data['breed'])

    def test_gender_field_succes(self):
        data = self.serializer.data

        self.assertEqual(data['gender'], self.dog_data['gender'])

    def test_gender_field_fail(self):
        self.serializer_data['gender'] = 'male'

        serializer = serializers.DogSerializer(data=self.serializer_data)

        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors, ['gender'])

    def test_size_field_succes(self):
        data = self.serializer.data

        self.assertEqual(data['size'], self.dog_data['size'])

    def test_size_field_fail(self):
        self.serializer_data['size'] = 'small'

        serializer = serializers.DogSerializer(data=self.serializer_data)

        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors, ['size'])


class UserPrefSerializerTest(TestCase):
    def setUp(self):
        form = UserCreationForm(data={
            'id': 1,
            'username': 'crit',
            'password1': '123',
            'password2': '123'
        })
        form.save()
        self.user = User.objects.get(id=1)
        self.user_pref_data = {
            'user': self.user,
            'age': 'y',
            'gender': 'm',
            'size': 'm'
        }

        self.serializer_data = {
            'user': self.user,
            'age': 'y',
            'gender': 'm',
            'size': 'm'
        }

        self.user_pref = models.UserPref.objects.create(**self.user_pref_data)
        self.serializer = serializers.UserPrefSerializer(
            instance=self.user_pref)

    def test_age_field_succes(self):
        data = self.serializer.data

        self.assertEqual(data['age'], self.user_pref_data['age'])

    def test_age_field_fail(self):
        self.serializer_data['age'] = 20

        serializer = serializers.UserPrefSerializer(data=self.serializer_data)

        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors, ['age'])

    def test_gender_field_succes(self):
        data = self.serializer.data

        self.assertEqual(data['gender'], self.user_pref_data['gender'])

    def test_gender_field_fail(self):
        self.serializer_data['gender'] = 'male'

        serializer = serializers.UserPrefSerializer(data=self.serializer_data)

        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors, ['gender'])

    def test_size_field_succes(self):
        data = self.serializer.data

        self.assertEqual(data['size'], self.user_pref_data['size'])

    def test_size_field_fail(self):
        self.serializer_data['size'] = 'small'

        serializer = serializers.UserPrefSerializer(data=self.serializer_data)

        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors, ['size'])


class ViewsTests(TestCase):
    def setUp(self):
        form = UserCreationForm(data={
            'id': 1,
            'username': 'crit',
            'password1': '123',
            'password2': '123'
        })
        form.save()
        dog_one = {
            'name': 'one',
            'image_filename': '1.jpg',
            'age': 20,
            'breed': 'Labrador',
            'gender': 'm',
            'size': 'm',

        }
        dog_two = {
            'name': 'two',
            'image_filename': '2.jpg',
            'age': 20,
            'breed': 'Labrador',
            'gender': 'f',
            'size': 'm',

        }
        dog_three = {
            'name': 'three',
            'image_filename': '3.jpg',
            'age': 20,
            'breed': 'Labrador',
            'gender': 'm',
            'size': 'm',

        }
        self.dog_one = models.Dog.objects.create(**dog_one)
        self.dog_two = models.Dog.objects.create(**dog_two)
        self.dog_three = models.Dog.objects.create(**dog_three)
        self.user = User.objects.get(id=1)
        token = Token.objects.create(user=self.user).key
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def test_RetrieveUpdateUserPref_get(self):
        response = self.client.get('/api/user/preferences/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_RetrieveUpdateUserPref_put(self):
        response = self.client.put('/api/user/preferences/', {
            'id': 1,
            'age': 'y,b',
            'gender': 'm',
            'size': 'm'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, {
            'id': 1,
            'age': 'y,b',
            'gender': 'm',
            'size': 'm'
        })

    def test_UpdateDog_put(self):
        response = self.client.put('/api/dog/1/liked/', format='json')
        # raises exception if UserDog was not created
        user_dog = models.UserDog.objects.get(dog__id=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user_dog.status, 'l')

    def test_DetailDog_retrieve_undecided(self):
        self.client.put('/api/user/preferences/', {
            'id': 1,
            'age': 'y,b',
            'gender': 'm',
            'size': 'm'
        }, format='json')
        response_one = self.client.get(
            '/api/dog/-1/undecided/next/', format='json')
        response_two = self.client.get(
            '/api/dog/1/undecided/next/', format='json')
        response_three = self.client.get(
            '/api/dog/3/undecided/next/', format='json')

        self.assertEqual(response_one.status_code, status.HTTP_200_OK)
        # should return male dog based on preferences and skip dog #2
        self.assertEqual(response_two.status_code, status.HTTP_200_OK)
        self.assertEqual(response_two.data['gender'], 'm')
        # third call should return 404 - no more dogs in database
        self.assertEqual(response_three.status_code, status.HTTP_404_NOT_FOUND)

    def test_DetailDog_retrieve_liked_disliked(self):
        self.client.put('/api/dog/1/liked/', format='json')
        self.client.put('/api/dog/3/disliked/', format='json')
        response_one = self.client.get(
            '/api/dog/-1/liked/next/', format='json')
        response_three = self.client.get(
            '/api/dog/-1/disliked/next/', format='json')

        self.assertEqual(response_one.status_code, status.HTTP_200_OK)
        self.assertEqual(response_one.data['name'], 'one')
        self.assertEqual(response_three.status_code, status.HTTP_200_OK)
        self.assertEqual(response_three.data['name'], 'three')
