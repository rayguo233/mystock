from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from rest_framework.response import Response

@api_view(['POST'])
def sign_up(request):
    return JsonResponse(
        User.objects.create_user(
            username=request.POST['email'],
            password=request.POST['password'])
    )

@api_view(['GET'])
def who_am_i(request):
    return Response(request.user.username)
