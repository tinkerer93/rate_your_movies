from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=True, allow_blank=False, max_length=100)
    text = serializers.CharField(required=True, allow_blank=False, max_length=2000)
    date_published = serializers.DateTimeField(required=True)
    rating = serializers.IntegerField(allow_blank=True)

    def create(self, validated_data):
        return Post.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for key, attr in validated_data.items():
            setattr(instance, key, attr)
        instance.save()
        return instance