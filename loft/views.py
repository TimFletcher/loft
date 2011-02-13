from decorators import add_ajax
from django.shortcuts import get_object_or_404
from django import http

@add_ajax('loft/entry_detail.html')
def detail(request, klass, slug):
    
    """
    Simple decorated view to return either a rendered template or, if requested
    via AJAX, a JSON response. Note that we are returning queryset.values()
    rather than a serialized version of the object because we shouldn't be
    exposing every field in the json. values() can only be run on a queryset
    hence we use filter() rather than get().

    There are issues with this method. queryset.values() only works for model
    field attributes, not methods. If you need this functionality, you're
    probably better off using a decorator that serialises a dictionary that
    you build manually.
    """

    obj = klass._default_manager.filter(slug=slug)
    if not obj:
        raise http.Http404
    return {
        'object': obj[0],
        'object_json': obj.values(
            'title', 'excerpt_html', 'body_html', 'author', 'publish_date',
            'featured', 'slug'
        )
    }


@add_ajax('loft/entry_list.html')
def list(request, klass):
    obj_list = klass._default_manager.published()
    return {
        'object_list': obj_list,
        'object_list_json': obj_list.values(
            'title', 'excerpt_html', 'body_html', 'author', 'publish_date',
            'featured', 'slug'
        )
    }
