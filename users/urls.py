from django.urls import path
from . import views

urlpatterns = [
    path('', views.UsersView.as_view(), name='all_users'),
    path('<int:user_id>/', views.UserDetailView.as_view(), name='user_detail'),
    path('create/', views.CreateUserView.as_view(), name='create_user'),
    path('auth/', views.UserAuthenticationView.as_view(), name='user_auth')
]