from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.hashing import check_password, hash_password

from .models import AuthToken, CustomUser

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_repeat = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'patronymic',
            'password',
            'password_repeat'
        ]

    def validate(self, data):
        if data['password'] != data['password_repeat']:
            raise serializers.ValidationError("Пароли не совпадают")
        return data

    def create(self, validated_data):
        validated_data.pop('password_repeat')
        raw_password = validated_data.pop('password')
        hashed_password = hash_password(raw_password)
        user = User.objects.create(
            password=hashed_password,
            **validated_data
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(write_only=True, required=False)
    current_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'patronymic',
            'current_password',
            'new_password'
        ]

    def validate(self, attrs):
        user = self.instance
        new_password = attrs.get('new_password')
        current_password = attrs.get('current_password')
        if new_password:
            if not current_password:
                raise serializers.ValidationError(
                    "Требуется текущий пароль для изменения пароля."
                )
            if not check_password(current_password, user.password):
                raise serializers.ValidationError(
                    "Неверный текущий пароль."
                )
        return attrs

    def update(self, instance, validated_data):
        new_password = validated_data.pop('new_password', None)
        validated_data.pop('current_password', None)  # удаляем если есть
        if new_password:
            instance.password = hash_password(new_password)
        return super().update(instance, validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Неверный email или пароль")
        if not check_password(password, user.password):
            raise serializers.ValidationError("Неверный email или пароль")
        token = AuthToken.create_token(user=user)
        return {
            "user": user,
            "token": str(token.key),
        }


class UserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'patronymic',
            'role',
            'is_active',
            'date_joined'
        ]
        read_only_fields = ['date_joined']

    def validate_role(self, value):
        allowed_roles = ['admin', 'user']
        if value not in allowed_roles:
            raise serializers.ValidationError(
                f"Недопустимая роль: {value}"
                "Разрешены только: {', '.join(allowed_roles)}"
            )
        return value
