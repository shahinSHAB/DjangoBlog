from django import forms
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Blog, Category
from accounts.models import CustomUser


class BLogForm(forms.ModelForm):
    
    def __init__(self,*args,**kwargs):
        user = kwargs.pop('user')
        super().__init__(*args,**kwargs)
        self.fields['publish'].initial = timezone.now()
        self.fields['status'].initial = 'd'
        
        if not user.is_superuser:
            self.fields['author'].initial = user
            self.fields['author'].disabled = True
            
    publish = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={'type':'datetime-local'}))
    category = forms.ModelMultipleChoiceField(queryset=Category.objects.active())
            
    class Meta:
        model = Blog
        fields = (
            'title',
            'slug',
            'author',
            'content',
            'code',
            'publish',
            'thumbnail',
            'category',
            'special',
            'status',
        )
        widgets = {
            'content':forms.Textarea(attrs={'cols':100, 'rows':10, 'placeholder':'Text ...'}),
            'code':forms.NumberInput(attrs={'placeholder':'12345',}),
            'title':forms.TextInput(attrs={'placeholder':'Sample Article',}),
            'slug':forms.TextInput(attrs={'placeholder':'sample-article',}),
        }


class CategoryForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        
        if not user.is_superuser:
            self.fields['status'].initial = False
            self.fields['status'].disabled = True
    
    class Meta:
        model = Category
        fields = ('title', 'slug', 'position', 'parent', 'status')


class ProfileForm(forms.ModelForm):
    
    def __init__(self,*args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        
        self.fields['username'].help_text=None
        self.fields['phone'].initial = '00-000-0000'
        self.fields['postal_code'].initial = ''
        self.fields['mobile'].initial = ''
        self.fields['gender'].initial = 'u'
        self.fields['personal_info'].initial = ''
        self.fields['first_name'].initial = ''
        self.fields['last_name'].initial = ''
        self.fields['home_address'].initial = ''
        self.fields['age'].initial = 0
        self.fields['degree'].initial = ''

        if not user.is_superuser:
            self.fields['username'].disabled = True
            self.fields['email'].disabled = True
            self.fields['phone'].disabled = True

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'personal_info',
            'phone',
            'mobile',
            'home_address',
            'postal_code',
            'age',
            'gender',
            'degree',
        )


class SharePostForm(forms.Form):
    name = forms.CharField(max_length=150, required=False, empty_value='')
    email = forms.EmailField(max_length=250)
    message = forms.CharField(widget=forms.Textarea, empty_value='', required=False)
