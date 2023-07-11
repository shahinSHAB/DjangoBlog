from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

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
    name = models.CharField(_('name'), max_length=30, unique=True)
    text = models.TextField(_('text'), max_length=300)
    author = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('author'))
    article = models.ForeignKey(Blog, on_delete=models.CASCADE, blank=True, null=True, default=None ,
                                related_name='comments', verbose_name=_('article'))
    status = models.BooleanField(_('status'), default=False)
    publish = models.DateTimeField(_('publish'), default=timezone.now, blank=True, null=True)
    reply = models.ForeignKey('self', on_delete=models.CASCADE, default=None, null=True, blank=True,
                              related_name='replies', verbose_name=_('reply'))
    agree = models.PositiveSmallIntegerField(_('agree'), blank=True, default=0)
    disagree = models.PositiveSmallIntegerField(_('disagree'), blank=True, default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    objects = CommentManager()
    
    class Meta:
        ordering = ['-publish']
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
        
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('comments:detail', kwargs={"slug":self.article.slug, "pk": self.pk})
    
    
    def comment_replies(self):
        return self.replies.count()
    
    def published_replies(self):
        return self.replies.published().count()
