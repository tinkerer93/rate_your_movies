import jwt
from django.contrib.auth import user_logged_in, user_logged_out
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import Http404
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import jwt_payload_handler

from .models import User
from .serializers import UserSerializer
from rate_your_movies.settings import SECRET_KEY


def get_user_or_raise_404(**kwargs):
    try:
        user_details = User().get_user_by_params(**kwargs)
    except ObjectDoesNotExist:
        raise Http404("User does not exist.")
    return user_details


class CreateUserView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response("User with such credentials already exists.", status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersView(APIView):
    authentication_classes = [JSONWebTokenAuthentication]
    permission_classes = (AllowAny,)

    def get(self, request):
        user_list = User.objects.all()
        if len(user_list):
            serializer = UserSerializer(user_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise Http404("No users are available.")


class UserDetailView(APIView):
    authentication_classes = [JSONWebTokenAuthentication]

    def get(self, request, user_id):
        user = get_user_or_raise_404(pk=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_id):
        user = get_user_or_raise_404(pk=user_id)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.update(user, serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        user = get_user_or_raise_404(pk=user_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserAuthenticationView(APIView):
    permission_classes = (AllowAny,)

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


class UserLogoutView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            user_logged_out.send(sender=user.__class__, request=request, user=user)
            return Response("User was successfully logged out.", status=status.HTTP_200_OK)