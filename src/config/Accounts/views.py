from random import random
import logging
import redis
from django.contrib.auth import logout, get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.db.models import Q

from config import settings
from .serializers import RequestOTPSerializer, VerifyOTPSerializer, CustomUserSerializer
from .utils import send_otp_email, send_otp_sms, save_otp_to_redis, get_otp_from_redis, delete_otp, generate_otp


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    user = request.user
    return Response({
        "username": user.username,
        "role": user.role,
    })

logger = logging.getLogger(__name__)
User = get_user_model()
#-----------------------------------------------------------------------------------------------------------------------
                                #Template-view-for-render
#-----------------------------------------------------------------------------------------------------------------------
def login_view(request):
    return render(request,'accounts/login.html')# set redirect->??

def register(request):
    return render(request,'accounts/register.html')
#-----------------------------------------------------------------------------------------------------------------------
                                    #api-view-for-accounts
#-----------------------------------------------------------------------------------------------------------------------
class RequestOtpView(APIView):

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        contact = serializer.validated_data['contact']

        otp_code = generate_otp()

        try:
            save_otp_to_redis(contact, otp_code, expire_seconds=300)
        except Exception as e:
            logger.error(f"Redis Error: {e}")
            return Response({"detail": "مشکل در ذخیره‌سازی OTP."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if "@" in contact:
            sent = send_otp_email(contact, otp_code)
        else:
            sent = send_otp_sms(contact, otp_code)

        if not sent:
            logger.error(f"Failed to send OTP to {contact}")
            return Response({"detail": "خطا در ارسال کد تایید."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"detail": "کد تایید ارسال شد."}, status=status.HTTP_200_OK)

#-----------------------------------------------------------------------------------------------------------------------

User = get_user_model()
logger = logging.getLogger(__name__)

class VerifyOtpView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        contact = serializer.validated_data['contact']
        otp_code = serializer.validated_data['otp_code']

        try:
            stored_otp = get_otp_from_redis(contact)
        except Exception as e:
            logger.error(f"Redis Error: {e}")
            return Response({"detail": "مشکل در بازیابی OTP."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if stored_otp is None:
            return Response({"detail": "کد تایید یافت نشد یا منقضی شده است."}, status=status.HTTP_400_BAD_REQUEST)

        if stored_otp.decode() != otp_code:
            return Response({"detail": "کد تایید اشتباه است."}, status=status.HTTP_400_BAD_REQUEST)

        delete_otp(contact)

        try:
            user = User.objects.get(Q(phone_number=contact) | Q(email=contact))
        except User.DoesNotExist:
            return Response({"detail": "ابتدا باید ثبت نام کنید."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"User Fetch Error: {e}")
            return Response({"detail": "خطا در دریافت کاربر."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        login(request, user)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = JsonResponse({
            "detail": "ورود موفق",
        })


        response.set_cookie(
            key='access',
            value=access_token,
            httponly=True,
            secure=False,
            samesite='Lax'
        )
        response.set_cookie(
            key='refresh',
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite='Lax'
        )

        return response


#-----------------------------------------------------------------------------------------------------------------------
@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    def post(self, request):
        print("POST DATA:", request.data)
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "ثبت‌نام با موفقیت انجام شد.",
                "user_id": user.id }, status=201)
        print("ERRORS:", serializer.errors)
        return Response(serializer.errors, status=400)

#-----------------------------------------------------------------------------------------------------------------------
@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    def post(self, request):

        if request.user.is_authenticated and request.session.session_key:
            logout(request)
            return Response({"message": "شما از سشن لاگ‌اوت شدید."}, status=status.HTTP_200_OK)

        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({"message": "توکن شما بلاک شد و لاگ‌اوت انجام شد."}, status=status.HTTP_200_OK)
            except Exception:
                return Response({"detail": "توکن معتبر نیست یا قبلاً بلاک شده است."}, status=status.HTTP_400_BAD_REQUEST)


        return Response({"detail": "نوع احراز هویت مشخص نیست."}, status=status.HTTP_400_BAD_REQUEST)
#-----------------------------------------------------------------------------------------------------------------------