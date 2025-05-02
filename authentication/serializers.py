from rest_framework import serializers
from .models import CustomUser, UserFace

class UserFaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFace
        fields = ['id', 'image', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)

class EmailCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)
    user_id = serializers.IntegerField(required=False)

class CustomUserSerializer(serializers.ModelSerializer):
    face = UserFaceSerializer(read_only=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    face_image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'password',
            'is_active', 'is_staff',
            'email_verified', 'face_verified',
            'email_code', 'email_code_expires',
            'face', 'face_image',
        ]
        read_only_fields = [
            'id', 'is_active', 'is_staff',
            'email_verified', 'face_verified', 'face',
            'email_code', 'email_code_expires',
        ]
    
    def create(self, validated_data):
        # On extrait le mot de passe des données validées
        password = validated_data.pop('password', None)
        
        # Retirer face_image s'il existe, car ce n'est pas un champ du modèle
        face_image = validated_data.pop('face_image', None)
        
        # On crée l'utilisateur sans le mot de passe
        instance = self.Meta.model(**validated_data)
        
        # Si un mot de passe est fourni, on le définit et on le hache
        if password is not None:
            instance.set_password(password)
        
        # On sauvegarde l'utilisateur
        instance.save()
        
        # L'image du visage sera traitée dans la vue
        
        return instance