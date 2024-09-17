from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, UserSerializer, CustomTokenRefreshSerializer, ForgotPasswordSerializer, VerifyResetCodeSerializer, ResetPasswordSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import Users
from .tasks import send_activation_code

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Send verification code logic can go here, e.g., via email or SMS.
            return Response({"message": "User registered successfully. Check your email for verification code."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyCodeView(APIView):
    def post(self, request):
        email = request.data.get('email')
        verification_code = request.data.get('verification_code')
        
        # Проверяем, что оба поля переданы
        if not email or not verification_code:
            return Response({"error": "Email and verification code are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Ищем пользователя по email и коду активации
            user = Users.objects.get(email=email, activation_code=verification_code)

            # Проверяем, не истек ли срок действия кода
            if user.is_code_valid():
                user.is_active = True
                user.save()
                return Response({"message": "User verified successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Verification code expired."}, status=status.HTTP_400_BAD_REQUEST)

        except Users.DoesNotExist:
            return Response({"error": "Invalid verification code or email."}, status=status.HTTP_400_BAD_REQUEST)



class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ForgotPasswordPhoneView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            # Получаем пользователя
            user = Users.objects.get(email=email)

            # Генерация нового кода верификации
            user.create_verification_code()
            user.save()

            # Отправляем код на телефон пользователя
            send_activation_code.delay(user.verification_code, user.email)

            return Response({"message": "Код для восстановления пароля отправлен на ваш номер телефона."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class VerifyResetCodeView(APIView):
    def post(self, request):
        serializer = VerifyResetCodeSerializer(data=request.data)
        if serializer.is_valid():
            verification_code = serializer.validated_data['verification_code']
            try:
                user = Users.objects.get(verification_code=verification_code)
            except Users.DoesNotExist:
                return Response({"error": "Invalid reset code."}, status=status.HTTP_400_BAD_REQUEST)

            if user.is_expired():
                return Response({"error": "Reset code has expired."}, status=status.HTTP_400_BAD_REQUEST)

            # # Очистка кода сброса и даты истечения
            # user.verification_code = ''  
            # user.expires_at = None
            # user.save()

            return Response({"message": "Reset code is valid and has been cleared. You can now set a new password."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            new_password = serializer.validated_data['new_password']

            # Обновление пароля пользователя
            user = Users.objects.get(email=email)
            user.set_password(new_password)
            user.verification_code = ''
            user.expires_at = None  # Очистка кода после успешного сброса пароля
            user.save()

            return Response({"message": "Пароль успешно изменен."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
