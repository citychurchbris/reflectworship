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
def filteractive(request, filtername, val):
    if request.GET.get(filtername, '') == val:
        return "active"
    return ""


@register.simple_tag
def root_url():
    return settings.ROOT_URL


@register.simple_tag
def relative_url(value, field_name, urlencode=None):
    url = '?{}={}'.format(field_name, value)
    if urlencode:
        querystring = urlencode.split('&')
        filtered_querystring = filter(
            lambda p: p.split('=')[0] != field_name, querystring)
        encoded_querystring = '&'.join(filtered_querystring)
        url = '{}&{}'.format(url, encoded_querystring)
    return url
