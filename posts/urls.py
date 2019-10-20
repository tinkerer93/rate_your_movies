from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostsView.as_view(), name='all_posts'),
    path('<int:post_id>', views.PostDetailView.as_view(), name='post_detail'),
    path('create', views.CreatePostView.as_view(), name='create_post'),
    path('<int:post_id>/like', views.CreateLikeView.as_view(), name='create_like'),
    path('top', views.TopPostsView.as_view(), name='top_ten_posts')
]