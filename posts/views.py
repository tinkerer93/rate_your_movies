from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Post


class DetailView(APIView):

    def get(self, request, post_id):
        post_details = Post.objects.get(pk=post_id)
        if post_details:
            pass
