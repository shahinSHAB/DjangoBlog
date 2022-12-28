from django import template

from ..models import Category


register = template.Library()

@register.inclusion_tag('blog/partial/navbar_items.html',name='nav_items')
def nav_items():
    context = {
        'categories':Category.objects.active().filter(parent=None)
    }
    return context
    

