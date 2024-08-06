from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate  # Importa authenticate
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail


User = get_user_model()

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


class PasswordResetRequestAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(correo_electronico=email).first()
        if user:
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm') + f"?uid={uidb64}&token={token}"
            )

            # Genera el cuerpo del correo electrónico directamente en el código
            email_body = f"""
            Hola,

            Recibimos una solicitud para restablecer tu contraseña. Puedes hacerlo a través del siguiente enlace:

            {reset_url}

            Si no solicitaste este cambio, puedes ignorar este correo.

            Gracias,
            El equipo de soporte
            """
            
            send_mail(
                'Password Reset Request',
                email_body,
                'noreply@example.com',
                [email],
                fail_silently=False,
            )
            return Response({'message': 'Password reset email has been sent.'}, status=status.HTTP_200_OK)
        return Response({'error': 'Email not found'}, status=status.HTTP_400_BAD_REQUEST)



class PasswordResetConfirmAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password has been reset.'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid token or user ID'}, status=status.HTTP_400_BAD_REQUEST)
    permission_classes = [AllowAny]  # Permitir acceso sin autenticación

    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))  # Cambia force_text a force_str
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password has been reset.'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid token or user ID'}, status=status.HTTP_400_BAD_REQUEST)
    permission_classes = [AllowAny]  # Permitir acceso sin autenticación

    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))  # Cambia force_text a force_str
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password has been reset.'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid token or user ID'}, status=status.HTTP_400_BAD_REQUEST)

    permission_classes = [AllowAny]  # Permitir acceso sin autenticación

    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))  # Cambia force_text a force_str
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password has been reset.'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid token or user ID'}, status=status.HTTP_400_BAD_REQUEST)