import datetime
from django.db import models
from django.utils.functional import cached_property


class Post(models.Model):
    title = models.CharField(max_length=100)
    text = models.CharField(max_length=2000)
    date_published = models.DateTimeField()
    likes = models.IntegerField()
    rating = models.IntegerField(null=True)

    def get_post_by_id(self, post_id):
        return self.objects.get(pk=post_id)

    def get_posts_older_than_date(self, search_date):
        return self.objects.filter(self.date_published < search_date)

    @cached_property
    def get_posts_for_current_date(self):
        current_date = datetime.now()
        return self.objects.filter(self.date_published == current_date)

    @cached_property
    def get_top_ten_posts(self):
        return self.objects.order_by('-likes')[:10]