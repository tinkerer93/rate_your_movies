from django.db import models, transaction
from django.utils import timezone
from users.models import User


class Post(models.Model):
    title = models.CharField(max_length=100)
    text = models.CharField(max_length=2000)
    date_published = models.DateField(default=timezone.now)
    likes = models.IntegerField(default=0)
    rating = models.IntegerField()
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)

    def get_post_by_params(self, **kwargs):
        return self.__class__.objects.get(**kwargs)

    def add_like_to_post(self, post_id):
        with transaction.atomic():
            post = self.__class__.objects.get(pk=post_id)
            post.likes += 1
            post.save()

    def get_current_posts(self):
        current_date = timezone.now().date()
        return self.__class__.objects.filter(date_published=current_date)

    def get_top_ten_posts(self):
        return self.__class__.objects.order_by('-likes')[:10]
