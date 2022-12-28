from django.contrib.auth import get_user_model
from django.shortcuts import get_list_or_404, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.http import Http404
# from django.urls import reverse_lazy

from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from blog.models import Blog, Category
from comments.models import Comment
from .permissions import (
    IsSuperUser,
    IsSuperUserOrOwnerReadOnly,
    IsSpecialArticle,
    IsSuperUserOrStaff,
    IsSuperUserOrAuthor,
    IsSuperUserOrDraftStatus,
    IsSuperUserOrOwner,
)
from .serializers import (
    UserSerializer,
    BlogModelSerializer,
    CategoryModelSerializer,
    CommentModelSerializer
)


# ============== Users Api View =================
class UserApiView(ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'list':
            permission_classes = (IsAuthenticated, IsAdminUser)
        elif self.action == 'retrieve':
            permission_classes = (IsAuthenticated, IsAdminUser, IsSuperUserOrOwnerReadOnly)
        else:
            permission_classes = (IsSuperUser,)
        return [permission() for permission in permission_classes]
            
    
# ============== ArticleList Api View =================
class ArticleListApiView(generics.ListAPIView):
    """returns blog objects api with publish status

    Returns:
        API: list of published articles
    """
    serializer_class = BlogModelSerializer
    
    def get_queryset(self):
        search_param = self.request.GET.get('q')
        default_query = Blog.objects.published().select_related(
            'author').prefetch_related('category', 'hits')
        if search_param:
            return get_list_or_404(default_query.filter(
                Q(title__icontains=search_param) | Q(content__icontains=search_param)))
        else:
            return get_list_or_404(default_query)
    
    
# ============== ArticleDetail Api View =================
class ArticleDetailApiView(generics.RetrieveAPIView):
    """returns blog object api with publish status

    Returns:
        API: one article from published articles
    """
    queryset = Blog.objects.published().select_related(
        'author').prefetch_related('category')
    serializer_class = BlogModelSerializer
    permission_classes = (IsAuthenticated, IsSpecialArticle)
    lookup_field = 'slug'
    
    
# ============== AllArticles Api View =================
class AllArticlesApiView(generics.ListAPIView):
    """returns blog object api with any status

    Returns:
        API: list of all articles
    """
    serializer_class = BlogModelSerializer
    permission_classes = (IsAuthenticated, IsSuperUserOrStaff)
    
    def get_queryset(self):
        return get_list_or_404(Blog.objects.all().select_related(
            'author').prefetch_related('category'))

        
# ============== CreateArticle Api View =================
class CreateArticleApiView(generics.CreateAPIView):
    serializer_class = BlogModelSerializer
    permission_classes = (IsAuthenticated, IsSuperUserOrStaff, IsSuperUserOrAuthor)
    
    def get_queryset(self):
        return get_list_or_404(Blog.objects.all().select_related(
            'author').prefetch_related('category'))


# ============ Article Detail Update Delete Api View ==============
class ArticleDetailUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Blog.objects.all().select_related(
        'author').prefetch_related('category')
    serializer_class = BlogModelSerializer
    permission_classes = (IsAuthenticated, IsSuperUserOrDraftStatus)  
    lookup_field = 'slug'
    
      
# ============== CreateCategory Api View =================
class CreateCategoryApiView(generics.CreateAPIView):
    serializer_class = CategoryModelSerializer
    permission_classes = (IsAuthenticated, IsSuperUserOrAuthor)
    
    def get_queryset(self):
        return get_list_or_404(Category.objects.all().select_related('parent'))
    
    
# ============ Category Detail Update Delete Api View ==============
class CategoryDetailUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all().select_related('parent')
    serializer_class = CategoryModelSerializer
    permission_classes = (IsAuthenticated, IsSuperUserOrAuthor)
    lookup_field = 'slug'
    
    
# ============ Category Articles Api View ==============
class CategoryArticlesApiView(generics.ListAPIView):
    serializer_class = BlogModelSerializer
    permission_classes = (IsAuthenticated,)
    def get_object(self):
        obj_slug = self.kwargs.get('slug')
        return Category.objects.active().get(slug=obj_slug)
    
    def get_queryset(self):
        return get_list_or_404(self.get_object().blog_set.published())
    
    
# ============ Articles Period Api View ==============
class ArticlesPeriodApiView(generics.ListAPIView):
    serializer_class = BlogModelSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        q_set = Blog.objects.published()
        q_param = self.kwargs.get('slug')
        last_month = timezone.now() - timedelta(days=30)
        last_week = timezone.now() - timedelta(days=7)
        last_day = timezone.now() - timedelta(days=1)
        if q_param == 'last-month':
            return get_list_or_404(q_set, publish__gt=last_month)
        elif q_param == 'last-week':
            return get_list_or_404(q_set, publish__gt=last_week)
        elif q_param == 'last-day':
            return q_set.filter(publish__gt=last_day)
        elif q_param == 'last-five-articles':
            return q_set[:5]
        else:
            raise Http404
    
    
# ============ MostViewedArticles Api View ==============
class MostViewedArticlesApiView(generics.ListAPIView):
    serializer_class = BlogModelSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        q_set = Blog.objects.published().order_by('-view')
        q_param = self.kwargs.get('slug')
        last_month = timezone.now() - timedelta(days=30)
        last_week = timezone.now() - timedelta(days=7)
        last_day = timezone.now() - timedelta(days=1)
        if q_param == 'last-month':
            return get_list_or_404(q_set, publish__gt=last_month)
        elif q_param == 'last-week':
            return get_list_or_404(q_set, publish__gt=last_week)
        elif q_param == 'last-day':
            return q_set.filter(publish__gt=last_day)
        elif q_param == 'last-five-articles':
            return q_set[:5]
        else:
            raise Http404
    
    
# =============== Profile Detail Api View ================
class ProfileDetailApiView(generics.RetrieveAPIView):
    queryset = get_user_model().objects.active_users()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsSuperUserOrOwner)
    lookup_field = 'username'
    
    
# =============== Profile Update Api View ================
class ProfileUpdateApiView(generics.RetrieveUpdateAPIView):
    queryset = get_user_model().objects.active_users()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsSuperUserOrOwner)
    lookup_field = 'username'
    
    
# =============== Author Information Api View ================
class AuthorInformationApiView(generics.ListAPIView):
    serializer_class = BlogModelSerializer
        
    def get_object(self):
        obj_username = self.kwargs.get('username')
        return get_user_model().objects.author_users().get(username=obj_username)
    
    def get_queryset(self):
        return get_list_or_404(self.get_object().blog_set.published())
    
    
# ================ Article Comments Api View ================
class ArticleCommentsApiView(generics.ListAPIView):
    serializer_class = CommentModelSerializer
    permission_classes = (IsAuthenticated, IsSuperUserOrStaff)
    
    def get_object(self):
        obj_slug = self.kwargs.get('slug')
        return get_object_or_404(Blog.objects.published(), slug=obj_slug)

    def get_queryset(self):
        return get_list_or_404(self.get_object().comments.all())


# ================ Published Comments Api View ================
class PublishedCommentsApiView(generics.ListAPIView):
    serializer_class = CommentModelSerializer
    permission_classes = (IsAuthenticated, IsSuperUserOrStaff)
    
    def get_object(self):
        obj_slug = self.kwargs.get('slug')
        return get_object_or_404(Blog.objects.published(), slug=obj_slug)

    def get_queryset(self):
        return get_list_or_404(self.get_object().comments.published())


# ================== Comment Detail Api View =================
class CommentDetailApiView(generics.RetrieveAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentModelSerializer
    permission_classes = (IsAuthenticated, IsSuperUserOrStaff)
    lookup_field = 'pk'
    
    
# ================== Comment Create Api View =================
class CommentCreateApiView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentModelSerializer
    
    
# ================== Comment Update Api View =================
class CommentUpdateApiView(generics.RetrieveUpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentModelSerializer
    permission_classes = (IsAuthenticated, IsSuperUserOrStaff)
    lookup_field = 'pk'
    
    
# ================== Comment Delete Api View =================
class CommentDeleteApiView(generics.RetrieveDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentModelSerializer
    permission_classes = (IsAuthenticated, IsSuperUserOrStaff)
    lookup_field = 'pk'
    
    
