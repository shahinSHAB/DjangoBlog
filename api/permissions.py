from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperUser(BasePermission):
    """if user is superuser then user can get the page
    and have full access.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_superuser
        )
        
        
class IsSuperUserOrOwnerReadOnly(BasePermission):
    """if user is superuser then user can get the page
    and have full access. if user is owner of object then 
    user can only read access ('GET' method).
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.method in SAFE_METHODS and request.user == obj:
            return True
        else:
            return False
            
            
class IsSuperUserOrOwner(BasePermission):
    """if user is superuser or user is owner of object then 
    user  then user can get the page and have full access.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user == obj:
            return True
        else:
            return False
            
            
class IsSuperUserOrStaff(BasePermission):
    """if user is superuser or user is staff then user can
    access the page.
    """
    def has_permission(self, request, view):
        if request.user.is_superuser or request.user.is_staff:
            return True
        else:
            return False
            
            
class IsSuperUserOrAuthor(BasePermission):
    """if user is superuser or user is author then user can
    access the page.
    """
    def has_permission(self, request, view):
        if request.user.is_superuser or request.user.is_author:
            return True
        else:
            return False
            
            
class IsSpecialArticle(BasePermission):
    """if article is special, only superusers, special users,
    and authors of article can access the page. 
    """
    def has_object_permission(self, request, view, obj):
        if obj.special is True:
            if request.user.is_superuser or obj.author == request.user or request.user.is_special_user():
                return True
            else:
                return False
        else:
            return True
        
        
class IsSuperUserOrDraftStatus(BasePermission):
    """if user is superuser or user is author and
    user is owner of object and object status is 
    'd' or 'b' then user can access the page.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return bool((request.user.is_author and request.user == obj.author) and obj.status in ['d', 'b'] )


class IsSuperUserOrAuthorOwner(BasePermission):
    """if user is superuser or user is author and
    user is owner of object then user can get the page
    and have full access.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return bool(request.user.is_author and obj.author == request.user)