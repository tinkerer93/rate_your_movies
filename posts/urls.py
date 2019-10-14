from django.urls import path
from . import views

urlpatterns = [
    path('<int:post_id>/', views.detail, name='detail'),
    path('top-10/', views.top_10, name='top_10')
]