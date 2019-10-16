from django.urls import path
from . import views

urlpatterns = [
    path('', views.UsersView.as_view(), name='main'),
    path('<int:user_id>/', views.UserDetailView.as_view(), name='user_detail')
]