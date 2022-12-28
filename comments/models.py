from django.db import models
from django.utils import timezone
from django.urls import reverse

from config.settings.base import AUTH_USER_MODEL
from blog.models import Blog


# =========== CommentsManager ===========
class CommentManager(models.Manager):
    
    def published(self):
        return self.filter(status=True)
    
    def parents(self):
        return self.published().filter(reply=None)


# =========== Comment Model ============
class Comment(models.Model):
    name = models.CharField(max_length=30, unique=True)
    text = models.TextField(max_length=300)
    author = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(Blog, on_delete=models.CASCADE, blank=True, null=True, default=None , related_name='comments')
    status = models.BooleanField(default=False)
    publish = models.DateTimeField(default=timezone.now, blank=True, null=True)
    reply = models.ForeignKey('self', on_delete=models.CASCADE, default=None, null=True, blank=True, related_name='replies')
    agree = models.PositiveSmallIntegerField(blank=True, default=0)
    disagree = models.PositiveSmallIntegerField(blank=True, default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    objects = CommentManager()
    
    class Meta:
        ordering = ['-publish']
        
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('comments:detail', kwargs={"slug":self.article.slug, "pk": self.pk})
    
    
    def comment_replies(self):
        return self.replies.count()
    
    def published_replies(self):
        return self.replies.published().count()
        
    