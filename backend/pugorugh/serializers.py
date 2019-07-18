from django.contrib.auth import get_user_model

from rest_framework import serializers

from . import models


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = get_user_model().objects.create(
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = get_user_model()
        fields = '__all__'


class DogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Dog
        fields = ('name', 'image_filename', 'breed',
                  'age', 'gender', 'size', 'id')

    def validate_age(self, value):
        if value > 0:
            return value
        raise serializers.ValidationError('Age has to be positive number')

    def validate_gender(self, value):
        if value in ['m', 'f', 'u']:
            return value
        raise serializers.ValidationError('Gender value allowed: m, f, u')

    def validate_size(self, value):
        if value in ['s', 'm', 'l', 'xl', 'u']:
            return value
        raise serializers.ValidationError('Size value allowed: s, m, l, xl, u')


class UserPrefSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserPref
        fields = ('age', 'gender', 'size', 'id')

    def validate_age(self, value):
        for char in value.split(','):
            if char not in ['b', 'y', 'a', 's']:
                raise serializers.ValidationError(
                    'Gender value allowed: b, y, a, s')
        return value

    def validate_gender(self, value):
        for char in value.split(','):
            if char not in ['m', 'f']:
                raise serializers.ValidationError('Gender value allowed: m, f')
        return value

    def validate_size(self, value):
        for char in value.split(','):
            if char not in ['s', 'm', 'l', 'xl']:
                raise serializers.ValidationError(
                    'Gender value allowed: s, m, l, xl')
        return value
