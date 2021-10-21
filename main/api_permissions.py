from rest_framework import permissions


class IsfEMRAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.groups.filter(name='fEMR Admin').exists()


class IsAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.groups.filter(name='Admin').exists()


class IsManager(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.groups.filter(name='Manager').exists()


class IsAPIAllowed(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.groups.filter(name='API Allowed').exists()
