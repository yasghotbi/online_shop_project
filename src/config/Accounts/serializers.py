from .models import CustomUser
from django.contrib.auth.password_validation import validate_password
import re
from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class RequestOTPSerializer(serializers.Serializer):
    contact = serializers.CharField(help_text="ایمیل یا شماره تلفن دریافت کننده OTP")

    def validate_contact(self, value):
        if "@" in value:
            try:
                validate_email(value)
            except ValidationError:
                raise serializers.ValidationError("ایمیل وارد شده معتبر نیست.")
        else:
            if not re.match(r"^\d{10,15}$", value):
                raise serializers.ValidationError("شماره تلفن معتبر نیست (باید فقط عدد و حداقل ۱۰ رقم باشد).")
        return value


class VerifyOTPSerializer(serializers.Serializer):
    contact = serializers.CharField(help_text="ایمیل یا شماره تلفن")
    otp_code = serializers.CharField(help_text="کد OTP")


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'role', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "رمزهای عبور با هم تطابق ندارند"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user



