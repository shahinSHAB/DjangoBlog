from django.contrib.sitemaps import GenericSitemap

from .models import Blog


class PostSitemap(GenericSitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Blog.objects.published()

    def lastmod(self, item):
        return item.updated
