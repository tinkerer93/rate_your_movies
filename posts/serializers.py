from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=True, allow_blank=False, max_length=100)
    text = serializers.CharField(required=True, allow_blank=False, max_length=2000)
    date_published = serializers.DateTimeField(required=True)