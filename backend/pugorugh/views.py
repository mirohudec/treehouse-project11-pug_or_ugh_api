from django.contrib.auth import get_user_model

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.models.query_utils import Q
from rest_framework import permissions
from rest_framework.generics import (CreateAPIView, UpdateAPIView,
                                     RetrieveAPIView, RetrieveUpdateAPIView, DestroyAPIView)

from . import serializers
from . import models


class UserRegisterView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    model = get_user_model()
    serializer_class = serializers.UserSerializer


class UpdateDog(UpdateAPIView):
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer

    def get_object(self):
        status = {
            'liked': 'l',
            'disliked': 'd',
            'undecided': ''
        }
        pk = int(self.kwargs.get('pk'))
        filter = self.kwargs.get('filter')
        if pk > 0:
            dog = models.Dog.objects.get(pk=pk)
        try:
            user_dog = models.UserDog.objects.get(dog=dog)
            user_dog.status = status[filter]
            user_dog.save()
        except models.UserDog.DoesNotExist:
            models.UserDog.objects.create(
                dog=dog,
                user=self.request.user,
                status=status[filter]
            )
        return dog


class DetailDog(RetrieveAPIView):
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer

    def get_object(self):
        pk = int(self.kwargs.get('pk'))
        filter = self.kwargs.get('filter')
        user_pref = models.UserPref.objects.get(user=self.request.user)

        age = user_pref.age
        gender = user_pref.gender
        size = user_pref.size

        if filter == 'undecided':
            queryset = models.Dog.objects.filter(
                Q(pk__gt=pk) &
                Q(gender__in=gender.split(',')) &
                Q(size__in=size.split(','))
            )
            for item in queryset:
                if item.age < 12:
                    dog_age = 'b'
                elif item.age < 24:
                    dog_age = 'y'
                elif item.age < 72:
                    dog_age = 'a'
                else:
                    dog_age = 's'
                if dog_age in age:
                    try:
                        user_dog = models.UserDog.objects.filter(
                            Q(dog=item) & Q(user=self.request.user)).get()
                    except models.UserDog.DoesNotExist:
                        return item
            raise Http404
        if filter == 'liked':
            user_dog = models.UserDog.objects.order_by('dog_id').filter(
                Q(dog_id__gt=pk) &
                Q(user=self.request.user) &
                Q(status='l')
            ).first()
            if not user_dog:
                raise Http404
            return user_dog.dog

        if filter == 'disliked':
            user_dog = models.UserDog.objects.order_by('dog_id').filter(
                Q(dog_id__gt=pk) &
                Q(user=self.request.user) &
                Q(status='d')
            ).first()
            if not user_dog:
                raise Http404
            return user_dog.dog


class RetrieveUpdateUserPref(RetrieveUpdateAPIView):
    queryset = models.UserPref.objects.all()
    serializer_class = serializers.UserPrefSerializer

    def get_object(self):
        return models.UserPref.objects.get(user=self.request.user)
