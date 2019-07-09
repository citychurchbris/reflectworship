from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def navactive(request, url):
    if reverse(url) in request.path:
        return "active"
    return ""
