from django.http import HttpResponse
from .models import Post


def detail(request, post_id):
    return HttpResponse(f'Get some info about {post_id} post.')

def top_10(request):
    post_list = Post.get_top_ten_posts()