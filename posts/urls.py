from django.urls import path
from . import views

urlpatterns = [
    path('<int:post_id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('', views.PostsView.as_view(), name='all_posts')
]