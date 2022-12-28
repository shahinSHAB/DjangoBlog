from django import forms
from django.utils import timezone

from .models import Comment


class CommentForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        article = kwargs.pop('article')
        parent = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)
        
        self.fields['author'].initial = user
        self.fields['article'].initial = article
        self.fields['publish'].initial = timezone.now()
        self.fields['status'].initial = False
        self.fields['agree'].initial = 0
        self.fields['disagree'].initial = 0
        if parent:
            self.fields['reply'].initial = parent
        else:
            self.fields['reply'].initial = None
        if not user.is_superuser:
            self.fields['author'].disabled = True
            self.fields['article'].disabled = True
            self.fields['status'].disabled = True
            self.fields['reply'].disabled = True
            self.fields['publish'].disabled = True
            self.fields['agree'].disabled = True
            self.fields['disagree'].disabled = True
    
    class Meta:
        model = Comment
        fields = (
            'name',
            'text',
            'author',
            'article',
            'status',
            'publish',
            'reply',
            'agree',
            'disagree',
        )
        widgets = {
            'publish':forms.DateTimeInput(attrs={'type':'datetime-local'})
        }