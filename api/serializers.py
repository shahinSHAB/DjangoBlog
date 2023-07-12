from django.contrib.auth import get_user_model
from django.utils import timezone

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        obj_slug = self.context['view'].kwargs.get('slug')
        article = Blog.objects.get(slug=obj_slug)
        self.fields['publish'].initial = timezone.now()
        self.fields['author'].initial = request.user.id
        self.fields['article'].initial = article.id
        if not request.user.is_superuser:
            self.fields['publish'].read_only = True
            self.fields['agree'].read_only = True
            self.fields['disagree'].read_only = True
            self.fields['updated'].read_only = True
            self.fields['author'].read_only = True
            self.fields['article'].read_only = True
            self.fields['reply'].read_only = True
            self.fields['status'].read_only = True

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

    def create(self, validated_data):
        request = self.context.get('request')
        obj_slug = self.context['view'].kwargs.get('slug')
        article = Blog.objects.get(slug=obj_slug)
        if request.user.is_superuser:
            return Comment.objects.create(**validated_data)
        return Comment.objects.create(**validated_data,
                                    author=request.user, article=article)


# ================= Share Post Serializer =====================
class SharePostSerializer(serializers.Serializer):
    name = serializers.CharField(allow_blank=True, max_length=100, read_only=True)
    email = serializers.EmailField(max_length=100)
    message = serializers.CharField(allow_blank=True, max_length=400, read_only=True,
                                    style={'base_html': 'textarea.html'})
