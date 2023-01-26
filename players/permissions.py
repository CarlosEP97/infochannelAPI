# Django REST Framework
from rest_framework.permissions import BasePermission


class IsPlayerOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        print(obj.user)
        return request.user == obj.user