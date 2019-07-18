from django.contrib.auth.models import User
from django.db import models

from django.db.models.signals import post_save
from django.dispatch import receiver


class Dog(models.Model):
    name = models.CharField(max_length=255, blank=True)
    image_filename = models.CharField(max_length=255, blank=True)
    breed = models.CharField(max_length=255, blank=True)
    age = models.IntegerField(blank=True, default=1)
    # "m" for male, "f" for female, "u" for unknown
    gender = models.CharField(max_length=1, blank=True)
    # "s" for small, "m" for medium, "l" for large, "xl" for extra
    # large, "u" for unknown
    size = models.CharField(max_length=2, blank=True)


class UserDog(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    dog = models.ForeignKey(to=Dog, on_delete=models.CASCADE)
    # "l" for liked, "d" for disliked
    status = models.CharField(max_length=1)


class UserPref(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    # "b" for baby, "y" for young, "a" for adult, "s" for senior
    age = models.CharField(max_length=7, blank=True)
    # "m" for male, "f" for female
    gender = models.CharField(max_length=3, blank=True)
    # "s" for small, "m" for medium, "l" for large, "xl" for extra
    # large
    size = models.CharField(max_length=8, blank=True)


@receiver(post_save, sender=User)
def after_created(sender, instance, created, ** kwargs):
    if created:
        UserPref.objects.create(
            user=instance,
        )
