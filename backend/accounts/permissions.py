
from rest_framework.permissions import BasePermission


class IsAdminOrManager(BasePermission):
    """
    Allows system administrators and branch managers.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return (
            user.is_superuser
            or user.role in [
                "SUPER_ADMIN",
                "ADMIN",
                "BRANCH_MANAGER"
            ]
        )


class IsStaffMember(BasePermission):
    """
    Allows administrators, branch managers and staff.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return (
            user.is_superuser
            or user.role in [
                "SUPER_ADMIN",
                "ADMIN",
                "BRANCH_MANAGER",
                "STAFF"
            ]
        )


class IsBranchOrderMember(BasePermission):
    """
    Allows employees to access orders belonging
    to their assigned branch.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if user.role in ["SUPER_ADMIN", "ADMIN"]:
            return True

        return (
            user.role in ["BRANCH_MANAGER", "STAFF"]
            and user.branch_id is not None
        )

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser:
            return True

        if user.role in ["SUPER_ADMIN", "ADMIN"]:
            return True

        return (
            user.branch_id is not None
            and obj.branch_id == user.branch_id
        )


class IsBranchOrderManager(BasePermission):
    """
    Allows administrators and branch managers
    to perform management operations on orders.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return (
            user.is_superuser
            or user.role in [
                "SUPER_ADMIN",
                "ADMIN",
                "BRANCH_MANAGER"
            ]
        )

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser:
            return True

        if user.role in ["SUPER_ADMIN", "ADMIN"]:
            return True

        return (
            user.role == "BRANCH_MANAGER"
            and user.branch_id is not None
            and obj.branch_id == user.branch_id
        )
