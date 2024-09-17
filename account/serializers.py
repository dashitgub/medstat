from rest_framework import serializers
from django.contrib.auth import get_user_model
from .tasks import send_activation_code
from .models import Users
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer


User = get_user_model()
    
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        fields = ['first_name', 'last_name', 'email', 'password', 'password_confirm', 'age', 'year', 'month']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError('пороль не совподают.')
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        age = validated_data.get('age')
        email = validated_data.get('email')
        year = validated_data.get('year')
        month = validated_data.get('month')

        user = User(
            first_name=first_name,
            last_name=last_name,
            age=age,
            email=email,
            year=year,
            month=month
        )
        user.set_password(password)
        user.save()

        # Создаем запись PhoneNumberVerification с активационным кодом
        verification, created = Users.objects.get_or_create(
            email=user.email
        )
        if not created:
            verification.create_verification_code()  # Это вызовет метод create_verification_code() который создаст новый verification_code

        # Запускаем задачу Celery
        send_activation_code.delay(verification.verification_code, user.email)  # Изменено на 'phone_number'
        # print(verification.verification_code)
        return user
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'age', 'year', 'month', 'is_active', 'activation_code', 'expires_at']

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        return data
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Получаем стандартный токен
        token = super().get_token(user)

        # Добавляем кастомные поля в токен
        token['phone_number'] = user.phone_number
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Добавляем дополнительные данные в ответ
        data['user_id'] = self.user.id

        return data
    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=50)

    def validate_phone_number(self, value):
        if not Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email не найден.")
        return value

class VerifyResetCodeSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=50)
    verification_code = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = Users.objects.get(email=data['email'], verification_code=data['verification_code'])
        except Users.DoesNotExist:
            raise serializers.ValidationError("Неверный email или код.")
        
        if not user.is_code_valid():  # Проверка на истечение срока действия кода
            raise serializers.ValidationError("Код подтверждения истек.")
        
        return data
    
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=50)
    verification_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Пароли не совпадают.")
        
        try:
            user = Users.objects.get(email=data['email'], verification_code=data['verification_code'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Неверный номер телефона или код подтверждения.")
        
        if not user.is_code_valid():
            raise serializers.ValidationError("Код подтверждения истек.")
        
        return data
