from django.urls import path
from . import views
from detail import views
from django.contrib import admin
urlpatterns = [
    path('details/', views.user_details_view, name='user_details'),
    path('success/', views.success_page, name='success_page'),
    path('admin/', admin.site.urls)
    ]

