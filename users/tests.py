from mock import patch
from django.test import TestCase
from posts.models import Post
from posts.serializers import PostSerializer
from users.serializers import UserSerializer


class CreatePostViewTest(TestCase):
    @patch('users.serializers.validate_email', return_value="mock@gmail.com")
    @classmethod
    def setUp(cls):
        user = {
            "first_name": "Jonh",
            "last_name": "Doe",
            "email": "mock@gmail.com",
            "password": "12345"
        }
        serializer = UserSerializer
        serializer.save(user)

