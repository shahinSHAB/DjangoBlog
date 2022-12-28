from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from .models import Category

from .models import Blog, Category, IpAddress


class BlogAdmin(admin.ModelAdmin):
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'author':
            kwargs['queryset'] = get_user_model().objects.author_users()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            kwargs['queryset'] = Category.objects.active()
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    
    list_display = [
        'title',
        'slug',
        'author',
        'status',
        'publish_time',
        'code',
        'special',
        'view',
        'category_list',
        'picture',
    ]
    list_filter = [
        'author',
        'status',
        'publish',
        'special',
        'category',
    ]
    search_fields = ['title', 'slug', 'code',]
    prepopulated_fields = {'slug':('title',)}
    
    def picture(self, instance):
        return format_html(f"<img src='{instance.thumbnail.url}' alt='{instance.title}\
                           picture' style='width:50px;height:35px;border-radius:5px;'>")
    
    def category_list(self, instance):
        cat_list = [category.title for category in instance.category.active()]
        return cat_list
    
    
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'position', 'status',]
    list_filter = ['status',]
    search_fields = ['title', 'slug', 'position',]
    prepopulated_fields = {'slug': ('title',)}
    
    
class IpAddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'ip_address']
    search_fields = ['ip_address', 'id']
    
    
# Register your models here.
admin.site.register(Blog, BlogAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(IpAddress, IpAddressAdmin)