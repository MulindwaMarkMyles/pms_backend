from django.db import models
from django.contrib.auth.models import User
from core.models import Estate

class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    estates = models.ManyToManyField(Estate)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username