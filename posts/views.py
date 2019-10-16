from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post
from .serializers import PostSerializer


class PostsView(APIView):

    def get(self, request):
        posts_list = Post.objects.all()
        if len(posts_list):
            serializer = PostSerializer(posts_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise Http404("No posts are available.")


class PostDetailView(APIView):

    @staticmethod
    def get_post_or_raise_404(post_id):
        post = Post()
        post_details = post.get_post_by_id(post_id)
        if post_details.DoesNotExist:
            raise Http404("Post does not exist.")
        return post_details

    def get(self, request, post_id):
        post = self.get_post_or_raise_404(post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            return Response("Post was successfully created.", status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, post_id):
        post = self.get_post_or_raise_404(post_id)
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.update(serializer.validated_data)
            return Response("Post was successfully updated.", status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id):
        post = Post.get_post_by_id(post_id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


