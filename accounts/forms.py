from django.utils import timezone
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email','password1','password2')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username',
                  'email',
                  'is_author',
                  'first_name',
                  'last_name',
                  'phone',
                  'mobile',
                  'home_address',
                  'postal_code',
                  'age',
                  'gender',
                  'degree',
        )


class SignUpForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'password1',
            'password2',
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
