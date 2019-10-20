import os
import requests
from rest_framework import serializers
from .models import User


def validate_email(email):
    emailhunter_token = os.environ['EMAILHUNTER_API_KEY']
    validation_url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={emailhunter_token}"
    response = requests.get(validation_url).json()
    if response["data"]["result"] == "undeliverable":
        raise serializers.ValidationError("Email can't be verified.")
    return email


class UserSerializer(serializers.ModelSerializer):
    registration_date = serializers.ReadOnlyField()
    email = serializers.EmailField(validators=[validate_email])
    posts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta(object):
        model = User
        fields = ('id', 'first_name', 'last_name', 'registration_date', 'email', 'password', 'posts')
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validated_data):
        for key, attr in validated_data.items():
            setattr(instance, key, attr)
        instance.save()
        return instance
