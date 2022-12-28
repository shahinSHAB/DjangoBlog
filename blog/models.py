from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse

from accounts.models import CustomUser


# =========== Custom Blog Manager ============
class BlogManager(models.Manager):
    
    def published(self):
        return self.filter(status=Blog.PUBLISH)


# =========== Custom Category Manager ============
class CategoryManager(models.Manager):
    
    def active(self):
        return self.filter(status=True)


# ========= IpAddress Model =============
class IpAddress(models.Model):
    ip_address = models.GenericIPAddressField()
    
    class Meta:
        verbose_name_plural = 'ips'
    
    def __str__(self):
        return self.ip_address
    
     
# ========= Category Model =============
class Category(models.Model):
    title = models.CharField(max_length=150,)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='sub_categories',
        blank=True,
        null=True,
        default=None,
    )
    position = models.PositiveSmallIntegerField(
        unique=True,
        validators=[MinValueValidator(1)],
    )
    status = models.BooleanField(default=False)

    # Custom manager
    objects = CategoryManager()

    class Meta:
        ordering = ['parent__id', 'position']
        verbose_name_plural='categories'

    def __str__(self):
        return self.title


# =========== Blog Model =============
class Blog(models.Model):
    DRAFT = 'd'
    PUBLISH = 'p'
    INVESTIGATION = 'i'
    BACK = 'b'
    CHOICES = (
        (DRAFT, 'draft'),
        (PUBLISH, 'publish'),
        (INVESTIGATION, 'investigation'),
        (BACK, 'back'),
    )
    title = models.CharField(max_length=150,)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    category = models.ManyToManyField(Category)
    code = models.PositiveIntegerField(
        unique=True,
        validators=[MinValueValidator(10000), ],
        help_text='please enter five digit number or more'
    )
    view = models.PositiveIntegerField(default=0)
    hits = models.ManyToManyField(IpAddress,related_name='hits',blank=True,through='ArticleView')
    thumbnail = models.ImageField(upload_to='images')
    publish = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=1, choices=CHOICES, default=DRAFT)
    special = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Custom manager
    objects = BlogManager()

    class Meta:
        ordering = ['-publish', '-status', 'title']
    
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={"slug": str(self.slug)})
    
    def __str__(self):
        return self.title
    
    def publish_time(self):
        self.publish = timezone.localtime(self.publish)
        return f'{self.publish.year}-{self.publish.month}-{self.publish.day} &\
                {self.publish.hour}:{self.publish.minute}:{self.publish.second}'

    def thumbnail_tag(self):
        return format_html(f"<img src='{self.thumbnail.url}' alt='{self.title}\
                           picture' style='width:100px;height:70px;border-radius:5px;'>")
        
    def status_full_name(self):
        if self.status == self.DRAFT:
            return 'draft'
        elif self.status == self.PUBLISH:
            return 'publish'
        elif self.status == self.INVESTIGATION:
            return 'investigation'
        elif self.status == self.BACK:
            return 'back'
        

# =========== ArticleView Through Model =============
class ArticleView(models.Model):
    articles = models.ForeignKey(Blog, on_delete=models.CASCADE)
    ip_address = models.ForeignKey(IpAddress, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    
