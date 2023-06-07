from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy
from django.template.defaultfilters import truncatewords_html

from .models import Blog


class LatestPostFeed(Feed):
    title = 'My Blog'
    link = reverse_lazy('blog:articles')
    description = 'new posts of my blog'

    def items(self):
        return Blog.objects.published()[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return truncatewords_html(item.content, 25)

    def item_pubdate(self, item):
        return item.publish
