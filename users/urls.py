from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('<int:user_id>/', views.detail, name='user_detail')
]