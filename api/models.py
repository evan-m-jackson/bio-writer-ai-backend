from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class Users(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=255)
    last_name = models.CharField(_('last name'), max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class FieldChoices(models.Model):
    field = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.field

class UserFields(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    order_num = models.IntegerField()
    field = models.ForeignKey(FieldChoices, on_delete=models.CASCADE)
    years = models.IntegerField()

    class Meta:
        unique_together = ['user', 'order_num']

class UserAchievements(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    achievements = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.first_name}'s achievement: {self.achievements}"

class UserBio(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    bio = models.TextField()

    def __str__(self):
        return f"{self.user.first_name}'s bio"
