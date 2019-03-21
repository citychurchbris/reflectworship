from django.utils.html import format_html


def url_to_link(url):
    return format_html("<a href='{url}'>{url}</a>", url=url)
