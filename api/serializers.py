from django.contrib.auth import get_user_model

from rest_framework import serializers

from blog.models import Blog, Category
from comments.models import Comment


# ============= User Model Serializer ================
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'special_user',
            'is_author',
            'phone',
            'mobile',
            'home_address',
            'postal_code',
            'personal_info',
            'age',
            'gender',
            'degree',
        )


# ============= Category Model Serializer ================
class CategoryModelSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = (
            'id',
            'title',
            'slug',
            'parent',
            'position',
            'status',
        )

    
# ============= Blog Model Serializer ================
class BlogModelSerializer(serializers.ModelSerializer):
    
    def author_username(self, instance):
        """returns username of author from each instance
        Args:
            instance (BLog object): each Blog object is an article
        Returns:
            str: username of article's author
        """
        return instance.author.username
    
    def thumbnail_path(self, instance):
        """returns path of thumbnail from each instance
        Args:
            instance (BLog object): each Blog object is an article
        Returns:
            Url: url of article's thumbnail
        """
        return instance.thumbnail.url
    
    def category_title(self, instance):
        """returns title of all active categories from each instance
        Args:
            instance (BLog object): each Blog object is an article
        Returns:
            List: titles of article's categories
        """
        active_categories = instance.category.active()
        return [category.title for category in active_categories]
    
    author = serializers.SerializerMethodField(method_name='author_username')
    thumbnail = serializers.SerializerMethodField(method_name='thumbnail_path')
    category = serializers.SerializerMethodField(method_name='category_title')
    class Meta:
        model = Blog
        fields = (
            'id',
            'title',
            'slug',
            'author',
            'content',
            'category',
            'code',
            'thumbnail',
            'view',
            'publish',
            'status',
            'special',
        )


# ============ Comment Model Serializer ==============
class CommentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            'id',
            'name',
            'text',
            'author',
            'article',
            'status',
            'publish',
            'reply',
            'agree',
            'disagree',
            'updated',
        )  