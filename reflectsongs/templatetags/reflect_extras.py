from django import template
from django.conf import settings
from django.urls import reverse

register = template.Library()


@register.simple_tag
def navactive(request, url):
    if reverse(url) in request.path:
        return "active"
    return ""


@register.simple_tag
def root_url():
    return settings.ROOT_URL
