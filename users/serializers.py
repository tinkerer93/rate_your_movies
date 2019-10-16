from rest_framework import serializers
from .models import User


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(required=True, allow_blank=False, max_length=50)
    last_name = serializers.CharField(required=True, allow_blank=False, max_length=50)
    email = serializers.EmailField(required=True, allow_blank=False)

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for key, attr in validated_data.items():
            setattr(instance, key, attr)
        instance.save()
        return instance

