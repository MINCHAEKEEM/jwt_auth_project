from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    nickname = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.username
