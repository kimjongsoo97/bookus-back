from django.db import models
from django.contrib.auth.models import PermissionsMixin,AbstractBaseUser,BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):
        email=self.normalize_email(email)
        user=self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser,PermissionsMixin):
    email=models.EmailField(max_length=50,unique=True,null=False)
    nickname=models.CharField(max_length=10,null=False,unique=True)
    name=models.CharField(max_length=50,null=False)
    phone_number=models.CharField(max_length=13,null=False)
    kakao_id=models.CharField(max_length=255,unique=True,null=True)
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

    objects=UserManager()
    def __str__(self):
         return f"[{self.id}] {self.nickname} <{self.email}>"    
