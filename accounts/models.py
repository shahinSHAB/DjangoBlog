from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone
from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):
    
    def active_users(self):
        return self.filter(is_active=True)
    
    def male_users(self):
        return self.filter(gender='m')
    
    def female_users(self):
        return self.filter(gender='f')
    
    def special_users(self):
        return self.filter(is_special_user=True)
    
    def author_users(self):
        return self.filter(is_author=True)


class CustomUser(AbstractUser):
    UNKNOWN = 'u'
    MALE = 'm'
    FEMALE = 'f'
    CHOICES = (
        (UNKNOWN, _('unknown')),
        (MALE, _('male')),
        (FEMALE, _('female')),
    )
    is_author = models.BooleanField(_('is_author'), default=False)
    special_user = models.DateTimeField(_('special user'), default=timezone.now)
    email = models.EmailField(_('email'), unique=True)
    personal_info = models.TextField(_('personal info'), max_length=700, blank=True, default='')
    phone = models.CharField(_('phone'), max_length=20, blank=True, default='00-000-0000')
    mobile = models.CharField(_('mobile'), max_length=20, blank=True, default='0935-648-7252')
    home_address = models.TextField(_('home address'), blank=True,max_length=400, default='')
    postal_code = models.SlugField(_('postal code'), blank=True, default='94-188-54587')
    age = models.PositiveSmallIntegerField(_('age'), blank=True, default=0)
    gender = models.CharField(_('gender'), max_length=1, choices=CHOICES, default=UNKNOWN, blank=True)
    degree = models.CharField(_('degree'), max_length=20, blank=True, default='')
    
    objects = CustomUserManager()
    
    class Meta:
        ordering = ['-date_joined', 'is_author']

    @admin.display(boolean=True)
    def is_special_user(self):
        """check the user is special or not

        Returns:
            boolean: yes or not
        """

        if self.special_user > timezone.now():
            return True
        else:
            return False
        
    def __str__(self):
        return self.username
    
    def gender_full_name(self):
        if self.gender == self.MALE:
            return 'male'
        elif self.gender == self.FEMALE:
            return 'female'
        elif self.gender == self.UNKNOWN:
            return 'unknown'
