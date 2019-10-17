from rest_framework import serializers
from .models import Post


def validate_rating(rating):
    if 1 > rating > 10 and not isinstance(rating, int):
        raise serializers.ValidationError("Rating is invalid.")
    return rating


class PostSerializer(serializers.Serializer):
    date_published = serializers.ReadOnlyField()
    rating = serializers.IntegerField(validators=[validate_rating])

    class Meta(object):
        model = Post
        fields = ('id', 'title', 'text', 'rating', 'author')

    def create(self, validated_data):
        return Post.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for key, attr in validated_data.items():
            setattr(instance, key, attr)
        instance.save()
        return instance