from decorators import add_ajax
from django.shortcuts import get_object_or_404
from django import http

@add_ajax('loft/entry_detail.html')
def detail(request, klass, slug):
    
    """
    Simple decorated view to return either a rendered template or, if requested
    via AJAX, a JSON response. Note that in order to get queryset.values() for
    the json response for a single object, we user filter() rather than get().
    """

    obj = klass._default_manager.filter(slug=slug)
    if not obj:
        raise http.Http404
    return {
        'object': obj[0],
        'object_json': obj.values(
            'title', 'excerpt_html', 'body_html', 'author', 'created',
            'featured', 'slug'
        )
    }


@add_ajax('loft/entry_list.html')
def list(request, klass):
    obj_list = klass._default_manager.all()
    return {
        'object_list': obj_list,
        'object_list_json': obj_list.values(
            'title', 'excerpt_html', 'body_html', 'author', 'created',
            'featured', 'slug'
        )
    }