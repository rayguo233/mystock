from rest_framework.authtoken import views
from django.urls import path
from .views import create_user, who_am_i

urlpatterns = [
    path('log-in/', views.obtain_auth_token),
    path('create-user/', create_user),
    path('who-am-i/', who_am_i)
]