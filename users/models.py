from django.db import models
from django.utils.functional import cached_property
from posts.models import Post


class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    registration_date = models.DateTimeField()
    email = models.EmailField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, related_name="author")

    @cached_property
    def get_number_of_posts_by_user(self):
        return self.post.count()

    @cached_property
    def get_top_ten_posts_by_user(self):
        return self.objects.select_related('Post').get_top_ten_posts()

    @cached_property
    def get_current_posts_by_user(self):
        return self.objects.select_related('Post').get_posts_for_current_date()
