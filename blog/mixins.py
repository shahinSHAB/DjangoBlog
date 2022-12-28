from django.http import Http404

from .models import Blog


class SuperUserAccessMixin:
    """if user is superuser then user
    can access the page otherwise get an Error404
    """
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404('Sorry you cant access this page')
 
        
class SuperUserOrAuthorAccessMixin:
    """if user is superuser or user is author then user
    can access the page otherwise get an Error404
    """
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser or user.is_author:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404('Sorry you cant access this page')
 

class SuperUserOrOwnerAccessMixin:
    """if user is superuser or user is author and owner of article
    then user can access the page otherwise get an Error404
    """
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        obj_slug = kwargs.get('slug')
        obj = Blog.objects.get(slug=obj_slug)
        if user.is_superuser or (user.is_author and obj.author == user):
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404('Sorry you cant access this page')

       
class SuperUserOrOwnerDraftAccessMixin:
    """if user is superuser or user is author and owner of article
    and also status of article is "d" or "b" then user can access
    the page otherwise get an Error404
    """
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        obj = self.get_object()
        if user.is_superuser or (obj.author == user and obj.status in ['d', 'b']):
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404('Sorry You Cant Access This Page')
 
        
class FormValidMixin:
    """if user is not superuser then author of article replace with
    this user and if status of article not "i" or "d" replace with "d"
    """
    
    def form_valid(self, form):
        if self.request.user.is_superuser:
            form.save()
        else:
            self.obj = form.save(commit=False)
            self.obj.author = self.request.user
            if self.obj.status not in ['i', 'd']:
                self.obj.status = 'd'
        return super().form_valid(form)
            
