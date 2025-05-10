from rest_framework.permissions import BasePermission
from Vendors.models import Store, Employee

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Store):
            return obj.owner == request.user
        return False

class IsEmployee(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Employee):
            return obj.store.owner == request.user or obj.user == request.user
        return False