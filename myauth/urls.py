from rest_framework.authtoken import views
from django.urls import path
from .views import sign_up, who_am_i

urlpatterns = [
    path('log-in/', views.obtain_auth_token),
    path('sign-up/', sign_up),
    path('who-am-i/', who_am_i)
]