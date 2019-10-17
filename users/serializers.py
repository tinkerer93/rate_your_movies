from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    registration_date = serializers.ReadOnlyField()

    class Meta(object):
        model = User
        fields = ('id', 'first_name', 'last_name', 'registration_date', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validated_data):
        for key, attr in validated_data.items():
            setattr(instance, key, attr)
        instance.save()
        return instance
