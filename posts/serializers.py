from rest_framework import serializers
from .models import Post
from users.models import User


def validate_rating(rating):
    if any([rating < 1, rating > 10]):
        raise serializers.ValidationError("Rating is invalid.")
    return rating


class PostSerializer(serializers.ModelSerializer):
    date_published = serializers.ReadOnlyField()
    rating = serializers.IntegerField(validators=[validate_rating])
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    likes = serializers.ReadOnlyField()

    class Meta(object):
        model = Post
        fields = ('id', 'title', 'text', 'rating', 'author', 'date_published', 'likes')

    def create(self, validated_data):
        return Post.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for key, attr in validated_data.items():
            setattr(instance, key, attr)
        instance.save()
        return instance
