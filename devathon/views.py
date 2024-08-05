from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate  # Importa authenticate
from rest_framework import serializers

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Agregar campos personalizados al token
        token['email'] = user.correo_electronico
        return token

    def validate(self, attrs):
        credentials = {
            'correo_electronico': attrs.get('correo_electronico'),
            'password': attrs.get('password')
        }

        user = authenticate(**credentials)

        if user:
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')

            refresh = self.get_token(user)
            access = refresh.access_token

            return {
                'refresh': str(refresh),
                'access': str(access),
            }
        else:
            raise serializers.ValidationError('Invalid credentials.')

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
