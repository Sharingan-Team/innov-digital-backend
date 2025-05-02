from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.utils import timezone
from django.core.files.storage import default_storage
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from rest_framework_simplejwt.tokens import RefreshToken
import random
import uuid
import requests
import os

from .models import CustomUser, UserFace
from .serializers import CustomUserSerializer, UserLoginSerializer, EmailCodeSerializer

CustomUser = get_user_model()

def send_email_code(user):
    code = str(random.randint(100000, 999999))
    user.email_code = code
    user.email_code_expires = timezone.now() + timezone.timedelta(minutes=10)
    user.save()
    
    # Uncomment this when ready to actually send emails
    # try:
    #     subject = "Votre code de vérification"
    #     email_from = getattr(settings, 'EMAIL_FROM', 'no-reply@example.com')
    #     print(f"Sending email to {user.email} with code {code}")
    #     email = EmailMessage(
    #         subject,
    #         f"Code: {code}",
    #         email_from,
    #         [user.email],
    #     )
    #     email.send(fail_silently=False)
    #     return True
    # except Exception as e:
    #     print(f"Email send error: {e}")
    #     return False
    return True

class SignupView(APIView):
    def post(self, request):
        # Extraire l'image si elle existe dans la requête
        face_image = request.FILES.get('face_image', None)
        
        user_serializer = CustomUserSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            
            # Traiter l'image du visage si elle existe
            if face_image:
                # Créer un UserFace associé à l'utilisateur
                user_face = UserFace.objects.create(user=user, image=face_image)
                user.face = user_face
                user.save()
            
            # Générer et envoyer le code de vérification
            send_email_code(user)
            
            return Response({
                'message': 'Utilisateur créé. Veuillez vérifier votre email pour le code de vérification.',
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            
            if user:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                send_email_code(user)
                
                # Stocker l'ID de l'utilisateur dans la session pour la vérification ultérieure
                request.session['pre_2fa_user_id'] = user.id
                
                return Response({
                    'message': 'Authentification réussie, veuillez vérifier votre email pour le code de vérification.',
                    'user_id': user.id,
                    'access': access_token,         
                    'refresh': str(refresh),
                })
            return Response({'error': 'Identifiants invalides'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailCodeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user_id = request.user.id
        
        if not user_id:
            return Response({'error': 'User ID non fourni'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Code non fourni'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier si le code est valide et non expiré
        now = timezone.now()
        if code == user.email_code and user.email_code_expires and now < user.email_code_expires:
            user.email_verified = True
            user.save()
            return Response({
                'message': 'Email vérifié, passez à la vérification du visage.',
                'email_verified': True,
                'user_id': user.id
            })
        
        if user.email_code_expires and now >= user.email_code_expires:
            return Response({'error': 'Code expiré'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error': 'Code invalide'}, status=status.HTTP_400_BAD_REQUEST)

class FaceEnrollmentView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        
        # user_id = request.session.get('pre_2fa_user_id') or request.data.get('user_id')
        user_id = request.user.id
        if not user_id:
            return Response({'error': 'User ID non fourni'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        
        face_image = request.FILES.get('face_image')
        if not face_image:
            return Response({'error': 'Image du visage non fournie'}, status=status.HTTP_400_BAD_REQUEST)
        
        if hasattr(user, 'face') and user.face:
            user.face.image = face_image
            user.face.save()
        else:
            user_face = UserFace.objects.create(user=user, image=face_image)
            user.face = user_face
            user.save()
        
        return Response({
            'message': 'Image du visage enregistrée avec succès.',
            'user_id': user.id
        })

class FaceVerificationView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        # user_id = request.session.get('pre_2fa_user_id') or request.data.get('user_id')
        user_id = request.user.id

        if not user_id:
            return Response({'error': 'User ID non fourni'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        
        # Vérifier si l'email a été vérifié
        if not user.email_verified:
            return Response({'error': 'Veuillez vérifier votre email avant de procéder à la vérification du visage'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier si l'utilisateur a une image de visage enregistrée
        if not hasattr(user, 'face') or not user.face or not user.face.image:
            return Response({'error': 'Aucune image de référence trouvée. Veuillez d\'abord enregistrer votre visage.'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Obtenir l'image live
        live_image = request.FILES.get('face_image')
        if not live_image:
            return Response({'error': 'Image du visage non fournie'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Sauvegarder l'image live temporairement
        temp_live_path = f"temp/live_{uuid.uuid4()}.jpg"
        default_storage.save(temp_live_path, live_image)
        live_image_full_path = default_storage.path(temp_live_path)
        
        # Obtenir l'image de référence
        reference_image_full_path = user.face.image.path
        
        try:
            # Préparer l'appel à l'API Face++
            api_url = 'https://api-us.faceplusplus.com/facepp/v3/compare'
            api_key = '0QW3oIVVzrsyJF91x56-wEtCuOBZGToh'  
            api_secret = 'ZVAqxq0-WPnGIr10IeqKM3OYe4yyddKE' 
            
            files = {
                'image_file1': open(reference_image_full_path, 'rb'),
                'image_file2': open(live_image_full_path, 'rb')
            }
            
            data = {
                'api_key': api_key,
                'api_secret': api_secret
            }
            
            response = requests.post(api_url, data=data, files=files)
            result = response.json()
            
            if 'confidence' in result:
                confidence = result['confidence']
                print(f"Face++ confidence score: {confidence}")
                
                if confidence > 70: 
                    user.face_verified = True
                    user.save()
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)

                    return Response({
                        'message': 'Visage vérifié, connexion réussie!',
                        'user_id': user.id,
                        'access': access_token,         
                        'refresh': str(refresh),
                    })
                else:
                    return Response({'error': 'La vérification du visage a échoué.'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'error': result.get('error_message', 'Erreur API Face++')}, 
                               status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({'error': f'Erreur lors de la vérification du visage: {str(e)}'}, 
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        finally:
            if 'files' in locals():
                if 'image_file1' in files:
                    files['image_file1'].close()
                if 'image_file2' in files:
                    files['image_file2'].close()
            
            if default_storage.exists(temp_live_path):
                default_storage.delete(temp_live_path)