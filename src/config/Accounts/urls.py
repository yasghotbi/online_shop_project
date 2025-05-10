from django.urls import path
from .views import RequestOtpView, VerifyOtpView, RegisterView, login_view, register, LogoutView, user_info

urlpatterns = [
    path('request-otp/', RequestOtpView.as_view(), name='request-otp'),
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('verify-otp/', VerifyOtpView.as_view(), name='verify-otp'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register_api/', RegisterView.as_view(), name='register_api'),
    path('me/', user_info),
    ]

