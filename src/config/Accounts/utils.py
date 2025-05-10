import re
from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden
import random
import requests
from django.conf import settings
from django.core.mail import send_mail
import redis
import logging
from rest_framework.exceptions import PermissionDenied



logger = logging.getLogger(__name__)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def generate_otp():
    return str(random.randint(100000, 999999))

def save_otp_to_redis(contact, otp, expire_seconds=600):
    redis_client.set(f"otp:{contact}", otp, ex=expire_seconds)

def get_otp_from_redis(contact):
    return redis_client.get(f"otp:{contact}")

def delete_otp(contact):
    redis_client.delete(f"otp:{contact}")

def send_otp_email(contact, otp_code):
    subject = "کد تأیید ورود"
    message = f"کد ورود شما: {otp_code}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [contact]
    sent_count = send_mail(subject, message, from_email, recipient_list)
    return sent_count > 0

def send_otp_sms(phone, otp):
    url = settings.TREZ_SMS_API_POST_URL
    payload = {
        "AccessHash": settings.TREZ_ACCESS_HASH,
        "Mobile": phone,
        "PatternId": settings.TREZ_PATTERN_ID,
        "token1": otp,
    }
    try:
        response = requests.post(url, data=payload, timeout=300)
        if response.status_code == 200:
            return True
        else:
            logger.error(f"SMS API error: {response.status_code} {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error in sending SMS: {str(e)}")
        return False

def update_user_group(user):
    previous_group = user.groups.first() if user.groups.exists() else None

    role_to_group = {
        'owner': 'owner',
        'employee': 'employee',
        'admin': 'admin',
        'customer': 'customer',
    }

    group_name = role_to_group.get(user.role, 'customer')
    new_group, created = Group.objects.get_or_create(name=group_name)

    if previous_group:
        user.groups.remove(previous_group)

    user.groups.add(new_group)
    user.save()




def is_valid_email(value):
    return re.match(r"[^@]+@[^@]+\.[^@]+", value)


class StoreAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        from Vendors.models import Store, Employee
        user = request.user
        try:
            self.store = Store.objects.get(owner=user, is_deleted=False)
            return super().dispatch(request, *args, **kwargs)
        except Store.DoesNotExist:
            pass
        try:
            employee = Employee.objects.get(user=user, is_deleted=False)
            self.store = employee.store
            return super().dispatch(request, *args, **kwargs)
        except Employee.DoesNotExist:
            pass
        raise PermissionDenied("شما به هیچ فروشگاهی دسترسی ندارید.")
