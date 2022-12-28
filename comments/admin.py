from django.contrib import admin

from .models import Comment


class CommentAdmin(admin.ModelAdmin):
    model = Comment
    list_display = [
        'name',
        'article',
        'agree',
        'reply',
        'disagree',
        'publish',
        'comment_replies',
        'published_replies',
        'status'
    ]
    list_filter = ['name', 'status', 'article']
    

admin.site.register(Comment, CommentAdmin)