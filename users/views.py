import jwt
from django.contrib.auth import user_logged_in
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.serializers import jwt_payload_handler

from .models import User
from .serializers import UserSerializer
from rate_your_movies.settings import SECRET_KEY


def get_user_or_raise_404(**kwargs):
    try:
        user_details = User.get_user_by_params(**kwargs)
    except ObjectDoesNotExist:
        raise Http404("User does not exist.")
    return user_details


class CreateUserView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("User was successfully created.", status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersView(APIView):
    def get(self, request):
        user_list = User.objects.all()
        if len(user_list):
            serializer = UserSerializer(user_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise Http404("No users are available.")


class UserDetailView(APIView):
    def get(self, request, id):
        user = self.get_user_or_raise_404(pk=id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        user = self.get_user_or_raise_404(pk=id)
        serializer = UserSerializer(user)
        if serializer.is_valid():
            serializer.update(serializer.validated_data)
            return Response("User was successfully updated.", status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        user = self.get_user_or_raise_404(pk=id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserAuthenticationView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        try:
            user = get_user_or_raise_404(email=email, password=password)
        except Http404:
            resp = {"error": "Cannot authenticate user with the credentials given."}
            return Response(resp, status=status.HTTP_403_FORBIDDEN)
        payload = jwt_payload_handler(user)
        token = jwt.encode(payload, SECRET_KEY)
        user_details = {}
        user_details['name'] = f"{user.first_name} {user.last_name}"
        user_details['token'] = token
        user_logged_in.send(sender=user.__class__, request=request, user=user)
        return Response(user_details, status=status.HTTP_200_OK)
