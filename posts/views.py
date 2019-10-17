from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from .models import Post
from .serializers import PostSerializer


def get_post_or_raise_404(post_id):
    try:
        post_details = Post().get_post_by_params(pk=post_id)
    except ObjectDoesNotExist:
        raise Http404("Post does not exist.")
    return post_details


class CreatePostView(APIView):
    authentication_classes = [JSONWebTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            return Response("Post was successfully created.", status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostsView(APIView):
    authentication_classes = [JSONWebTokenAuthentication]
    permission_classes = (AllowAny,)

    def get(self, request):
        posts_list = Post.objects.all()
        if len(posts_list):
            serializer = PostSerializer(posts_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise Http404("No posts are available.")


class PostDetailView(APIView):
    authentication_classes = [JSONWebTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        post = get_post_or_raise_404(post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, post_id):
        post = get_post_or_raise_404(post_id)
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.update(serializer.validated_data)
            return Response("Post was successfully updated.", status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id):
        post = get_post_or_raise_404(post_id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateLikeView(APIView):
    def put(self, request, post_id):
        post = get_post_or_raise_404(post_id)
        post.add_like_to_post(post_id)
        return Response(status=status.HTTP_200_OK)


class TopPostsView(APIView):
    def get(self, request):
        try:
            top_posts = Post().get_top_ten_posts()
        except ObjectDoesNotExist:
            return Response("No posts available", status=status.HTTP_404_NOT_FOUND)
        serializer = PostSerializer(top_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetCurrentPostsView(APIView):
    def get(self, request):
        try:
            current_posts = Post().get_current_posts()
        except ObjectDoesNotExist:
            return Response("No posts available", status=status.HTTP_404_NOT_FOUND)
        serializer = PostSerializer(current_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)