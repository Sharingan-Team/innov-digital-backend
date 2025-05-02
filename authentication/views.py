from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from .serializers import UserRegistrationSerializer
from .models import CustomUser
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class UserRegistrationView(generics.CreateAPIView):

    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer

    
user_registration_view = UserRegistrationView.as_view()