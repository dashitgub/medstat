from django.db import models
from django.utils import timezone 
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.crypto import get_random_string


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError('email - поле обязательное')
        email = self.normalize_email(email)
        first_name = extra.get('first_name')
        last_name = extra.get('last_name')
        age = extra.get('age')
        year = extra.get('year')
        month = extra.get('month')
        user = self.model(email=email, first_name=first_name, last_name=last_name, age=age, year=year, month=month)
        user.set_password(password)
        user.save()
        return user
    
    def create_user(self, email, password, **extra):
        user = self._create_user(email, password, **extra)
        user.create_code()
        user.save()
        return user
    
    def create_super_user(self, email, password, **extra):
        user = self._create_user(email, password, **extra)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save()
        return user
    
class Users(AbstractUser):
    first_name = models.CharField(max_length=30, verbose_name='имя')
    last_name = models.CharField(max_length=30, verbose_name='фамилия')
    email = models.EmailField(unique=True)
    age = models.DecimalField(max_digits=2, verbose_name='Возраст')
    year = models.DecimalField(max_digits=4, verbose_name='Год')
    month = models.DecimalField(max_digits=2)
    is_active = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=4, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def create_verification_code(self, *args, **kwargs):
            if not self.verification_code:
                self.verification_code = get_random_string(length=6, allowed_chars='0123456789')
            if not self.expires_at:
                self.expires_at = timezone.now() + timezone.timedelta(minutes=10)  # Установить время истечения срока действия
            super().save(*args, **kwargs)

    def is_code_valid(self):
        return timezone.now() < self.expires_at

    def is_expired(self):
        return timezone.now() > self.expires_at
        
    def __str__(self):
        return f"{self.email} - {self.verification_code}"
            