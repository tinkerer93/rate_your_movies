from django.shortcuts import render, get_object_or_404, get_list_or_404
from .models import User


def main(request):
    user_list = get_list_or_404(User.objects.order_by('-registration_date'))[:10]
    context = {'users': user_list}
    return render(request, 'users/main.html', context)


def detail(request, user_id):
    user_details = get_object_or_404(User, pk=user_id)
    context = {'user': user_details}
    return render(request, 'users/details.html', context)
