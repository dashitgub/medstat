# config/views.py
from django.shortcuts import render

def index(request):
    return render(request, 'base.html')

def user_details_view(request):
    # Здесь можно добавить логику для отображения деталей пользователя
    return render(request, 'details/base.html')