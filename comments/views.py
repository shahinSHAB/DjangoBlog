from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, get_list_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Comment
from .forms import CommentForm
from blog.models import Blog
from blog import mixins


# ============= Article Comments View =============
class ArticleCommentsView(LoginRequiredMixin, mixins.SuperUserAccessMixin, generic.ListView):
    context_object_name='comments'
    template_name='comments/article_comments.html'
    
    def get_object(self):
        obj_slug = self.kwargs.get('slug')
        return get_object_or_404(Blog.objects.published(), slug=obj_slug)
    
    def get_queryset(self):
        return get_list_or_404(self.get_object().comments.all())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['article'] = self.get_object()
        return context


# ============= Published Comments View =============
class PublishedCommentsView(LoginRequiredMixin, mixins.SuperUserAccessMixin, generic.ListView):
    context_object_name='comments'
    template_name='comments/published_comments.html'
    
    def get_object(self):
        obj_slug = self.kwargs.get('slug')
        return get_object_or_404(Blog.objects.published(), slug=obj_slug)
    
    def get_queryset(self):
        return get_list_or_404(self.get_object().comments.published())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['article'] = self.get_object()
        return context
    

# ============= Comment Detail View =============
class CommentDetailView(LoginRequiredMixin, mixins.SuperUserAccessMixin, generic.DetailView):
    context_object_name='comment'
    template_name='comments/comment_detail.html'
    
    def get_object(self):
        obj_pk = self.kwargs.get('pk')
        return get_object_or_404(Comment.objects.all(), pk=obj_pk)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj_slug = self.kwargs.get('slug')
        article = Blog.objects.published().get(slug=obj_slug)
        context['article'] = article
        return context


# ============= Comment Create View =============
class CommentCreateView(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    model = Comment
    template_name='comments/comment_create.html'
    form_class = CommentForm
    success_message = 'your comment was created successfully please wait until we confirm it'
    
    def get_success_url(self):
        if not self.request.user.is_superuser:
            obj_slug = self.kwargs.get('slug')
            return reverse_lazy('blog:detail', kwargs={'slug':obj_slug})
        else:
            return super().get_success_url()
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        obj_slug = self.kwargs.get('slug')
        comment_reply = self.kwargs.get('name')
        try:
            form_article = Blog.objects.published().get(slug=obj_slug)
        except:
            form_article = Blog.objects.published().get(slug=self.request.resolver_match.kwargs['slug'])
        try:
            form_comment = Comment.objects.published().get(name=comment_reply)
        except:
            form_comment = None
        user = self.request.user
        kwargs.update({'article':form_article, 'user':user, 'parent':form_comment})
        return kwargs


# ============= Comment Update View =============
class CommentUpdateView(LoginRequiredMixin, mixins.SuperUserAccessMixin, SuccessMessageMixin, generic.UpdateView):
    context_object_name='comment'
    template_name='comments/comment_update.html'
    form_class = CommentForm
    success_message = 'your comment was updated successfully'
    
    def get_object(self):
        obj_pk = self.kwargs.get('pk')
        return get_object_or_404(Comment.objects.all(), pk=obj_pk)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        obj_slug = self.kwargs.get('slug')
        article = Blog.objects.published().get(slug=obj_slug)
        user = self.request.user
        kwargs.update({'article': article, 'user': user})
        return kwargs


# ============= Comment Delete View =============
class CommentDeleteView(LoginRequiredMixin, mixins.SuperUserAccessMixin, SuccessMessageMixin, generic.DeleteView):
    context_object_name = 'comment'
    template_name = 'comments/comment_delete.html'
    success_message = 'your comment was delete successfully'
    
    def get_success_url(self):
        obj_slug = self.kwargs.get('slug')
        return reverse_lazy('comments:article_comments', kwargs={'slug':obj_slug})

    def get_object(self):
        obj_pk = self.kwargs.get('pk')
        return get_object_or_404(Comment.objects.all(), pk=obj_pk)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj_slug = self.kwargs.get('slug')
        article = Blog.objects.published().get(slug=obj_slug)
        context['article'] = article
        return context




