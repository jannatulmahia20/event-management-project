from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def group_required(*group_names):
    """
    Decorator for views that checks whether a user belongs to any of the specified groups,
    raises PermissionDenied if not.
    """
    def in_groups(user):
        if user.is_authenticated:
            if bool(user.groups.filter(name__in=group_names)) or user.is_superuser:
                return True
        raise PermissionDenied  
    return user_passes_test(in_groups)
