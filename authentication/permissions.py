from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from rest_framework import permissions


def user_is_contributor(user):
    return user.is_active and getattr(user, 'is_contributor', False)


def contributor_required(function=None, redirect_field_name=None, login_url=None):
    """
    Function decorator for contributor
    """
    actual_decorator = user_passes_test(
        user_is_contributor,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


class ContributorRequiredMixin(UserPassesTestMixin):
    """
    Class-based view mixin for contributor
    """
    def test_func(self):
        return user_is_contributor(self.request.user)


class IsContributor(permissions.BasePermission):
    """
    REST framework permission class for contributor
    """
    message = "You must be a verified Contributor to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'is_contributor', False)
        )
