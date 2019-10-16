from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer


class UserDetailView(APIView):

    @staticmethod
    def get_user_or_raise_404(user_id):
        user_details = User.get_user_by_id(user_id)
        if user_details.DoesNotExist:
            raise Http404("User does not exist.")
        return user_details

    def get(self, request, user_id):
        user = self.get_user_or_raise_404(user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            return Response("User was successfully created.", status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, user_id):
        user = self.get_user_or_raise_404(user_id)
        serializer = UserSerializer(user)
        if serializer.is_valid():
            serializer.update(serializer.validated_data)
            return Response("User was successfully updated.", status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        user = self.get_user_or_raise_404(user_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
