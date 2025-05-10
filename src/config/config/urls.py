"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.static import static # ایمپورت درست

from django.urls import path, include

from Cart.views import cart_view
from config import settings

urlpatterns = [

    path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('Accounts.urls')),
    path('api/vendors/', include('Vendors.urls')),
    path('', include('Website.urls')),
    path('account/', include('Customers.urls')),
    path('api/', include('Cart.urls')),
    path('shopping_cart/', cart_view, name='cart-page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)