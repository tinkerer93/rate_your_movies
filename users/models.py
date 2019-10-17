from django.db import models, transaction
from django.utils.functional import cached_property
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from posts.models import Post


class UserManager(BaseUserManager):

    def _create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError("The email must be set.")
        with transaction.atomic():
            user = self.model(email=email, **kwargs)
            user.set_password(password)
            user.save(using=self._db)
            return user

    def create_user(self, email, password=None, **kwargs):
        kwargs.setdefault("is_superuser", False)
        return self._create_user(email, password, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault("is_superuser", True)
        return self._create_user(email, password, **kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    registration_date = models.DateTimeField(default=timezone.now)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        return self

    @staticmethod
    def get_user_by_params(**kwargs):
        return User.objects.get(**kwargs)

    @cached_property
    def get_number_of_posts_by_user(self):
        return self.post.count()

    @cached_property
    def get_top_ten_posts_by_user(self):
        return self.objects.select_related('Post').get_top_ten_posts()

    @cached_property
    def get_current_posts_by_user(self):
        return self.objects.select_related('Post').get_posts_for_current_date()
