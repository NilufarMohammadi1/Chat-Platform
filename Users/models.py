from django.db import models
# import uuid
#
# class Users(models.Model):
#
#     class Meta:
#         db_table = "Users"
#
#     user_id = models.UUIDField(primary_key=True,default=uuid.uuid4(),editable=False)
#     nickname = models.CharField(max_length=100,blank=False,unique=False)
#     username = models.CharField(max_length=100,blank=False,unique=True)
#     password = models.CharField(max_length=128,blank=False)
#     join_date = models.DateTimeField(auto_now_add=True)
#     modified_at = models.DateTimeField(auto_now=True)
#     avatar = models.CharField(max_length=255,blank=True,unique=False)


from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class MyAccountManager(BaseUserManager):

    def create_user(self, nickname, username, password=None):
        if not username:
            raise ValueError('User must have a username')


        user = self.model(
            nickname=nickname,
            username = username,

        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, nickname, username, password):
        user = self.create_user(
            nickname=nickname,
            username=username,
            password = password
        )

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user



class Users(AbstractBaseUser):
    nickname = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    join_date = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['username']

    objects = MyAccountManager()

    class Meta:
        db_table = "Users"

    def full_name(self):
        return f'{self.username} known as {self.nickname}'

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True