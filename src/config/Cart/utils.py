import json
from django.conf import settings
import urllib.parse
#-----------------------------------------------------------------------------------------------------------------------
CART_COOKIE_NAME = 'cart'
CART_COOKIE_AGE = 60 * 60 * 24
#-----------------------------------------------------------------------------------------------------------------------
#save-cart-in-cookie-encode
def save_cart_to_cookie(response, cart_data):
    json_data = json.dumps(cart_data, separators=(',', ':'), ensure_ascii=False)
    encoded = urllib.parse.quote(json_data)
    response.set_cookie(
        CART_COOKIE_NAME,
        encoded,
        max_age=CART_COOKIE_AGE,
        httponly=True,
        samesite='Lax',
        secure=getattr(settings, 'SESSION_COOKIE_SECURE', False),
    )
    return response
#-----------------------------------------------------------------------------------------------------------------------
#get-cart-from-cookie-decode
def load_cart_from_cookie(request):
    raw = request.COOKIES.get(CART_COOKIE_NAME)
    try:
        decoded = urllib.parse.unquote(raw)
        data = json.loads(decoded)
        assert isinstance(data, dict) and 'items' in data
    except Exception:
        data = {'items': []}
    return data
#-----------------------------------------------------------------------------------------------------------------------
#clear-cart-after-order
def clear_cart_cookie(response):
    response.delete_cookie(
        CART_COOKIE_NAME,
        samesite='Lax',
    )
    return response
#-----------------------------------------------------------------------------------------------------------------------