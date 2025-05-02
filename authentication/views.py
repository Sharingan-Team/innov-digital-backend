from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser
from .serializers import *
import random
import requests
import os
from django.core.files.storage import default_storage
import uuid
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from django.contrib.auth import get_user_model
from .serializers import FaceVerificationSerializer



def send_email_code(user):
    code = str(random.randint(100000, 999999))
    user.email_code = code
    user.save()
    send_mail('Your verification code', f'Code: {code}', 'no-reply@secureauth.com', [user.email])

class SignupView(APIView):
    def post(self, request):
        user_serializer = UserRegistrationSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            send_email_code(user)
            request.session['signup_user_id'] = user.id  # Store user in session for next steps
            return Response({'message': 'User created. Please check your email for the verification code.'}, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username'],
                                password=serializer.validated_data['password'])
            if user:
                request.session['pre_2fa_user_id'] = user.id
                send_email_code(user)
                return Response({'message': 'Password OK, please verify email code.'})
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailCodeView(APIView):
    def post(self, request):
        user_id = request.session.get('pre_2fa_user_id')
        user = CustomUser.objects.get(id=user_id)
        serializer = EmailCodeSerializer(data=request.data)
        if serializer.is_valid() and serializer.validated_data['code'] == user.email_code:
            user.email_verified = True
            user.save()
            return Response({'message': 'Email verified, proceed to FaceID check.'})
        return Response({'error': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)

class FaceEnrollmentView(APIView):
    def post(self, request):
        # TEMPORARY: use a hardcoded user
        user = CustomUser.objects.get(username='testuser')

        serializer = FaceVerificationSerializer(data=request.data)
        if serializer.is_valid():
            face_image = serializer.validated_data['face_image']
            user.profile_image = face_image  # assign directly to ImageField
            user.save()
            return Response({'message': 'Face image enrolled successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

CustomUser = get_user_model()

class FaceVerificationView(APIView):
    def post(self, request):
        try:
            # TEMPORARY: use hardcoded test user for local testing
            user = CustomUser.objects.get(username='testuser')
        except CustomUser.DoesNotExist:
            return Response({'error': 'Test user does not exist. Please create it first.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FaceVerificationSerializer(data=request.data)
        if serializer.is_valid():
            live_image = serializer.validated_data['face_image']

            # Save live image temporarily
            temp_live_path = f"temp/live_{uuid.uuid4()}.jpg"
            default_storage.save(temp_live_path, live_image)
            live_image_full_path = default_storage.path(temp_live_path)

            # Get stored reference image
            reference_image_full_path = default_storage.path(user.face_image_path)

            # Prepare Face++ API call
            api_url = 'https://api-us.faceplusplus.com/facepp/v3/compare'
            api_key = ''
            api_secret = 'YOUR_FACEPP_API_SECRET'

            files = {
                'image_file1': open(reference_image_full_path, 'rb'),
                'image_file2': open(live_image_full_path, 'rb')
            }
            data = {
                'api_key': api_key,
                'api_secret': api_secret
            }

            try:
                response = requests.post(api_url, data=data, files=files)
                result = response.json()

                if 'confidence' in result:
                    confidence = result['confidence']
                    print(f"Face++ confidence score: {confidence}")

                    if confidence > 70:  # Adjust threshold as needed
                        return Response({'message': 'Face verified, login successful!'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Face verification failed.'}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    return Response({'error': result.get('error_message', 'Face++ API error')}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            finally:
                files['image_file1'].close()
                files['image_file2'].close()
                default_storage.delete(temp_live_path)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
