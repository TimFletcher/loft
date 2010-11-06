from django.template.loader import get_template
from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet, ValuesQuerySet
from django.db import models
from django import http
import json

class ValuesDjangoJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):

        """
        Enable serialisation of a ValuesQuerySet

        This function must return a serializable object for any object type it
        receives. ValuesQuerySet will return dictionaries when used as an
        iterable. Here we differentiate between a ValuesQuerySet with one or
        more items and return either a dictionary/list of dictionaries.

        You can test ajax queries from the terminal with:
        $ curl -H 'X-Requested-With: XMLHttpRequest' <url>

        Serialising querysets - returns a multiple item list
        if isinstance(obj, QuerySet):
            return json.loads(serializers.serialize('json', obj))
        
        Serialising models - returns a single item list
        if isinstance(obj, models.Model):
            obj = [obj] # Iterable required
            return json.loads(serializers.serialize("json", obj))[0]
        """

        if isinstance(obj, ValuesQuerySet):
            if len(obj) > 0:
                return list(obj)
            else:
                return list(obj)[0]
        return DjangoJSONEncoder.default(self, obj)

def add_ajax(template_name):

    """
    Decorator to render a response either with a template, as normal, or as
    JSON. All querysets and model instances are converted to JSON.
    """

    def decorator(view):
        def wrapper(request, *args, **kwargs):

            """ Find any ValuesQuerySets in the view's returned dictionary """

            data = view(request, *args, **kwargs)
            if request.is_ajax():
                for k,v in data.items():
                    if not isinstance(v, ValuesQuerySet):
                        del data[k]
                response = json.dumps(data, cls=ValuesDjangoJSONEncoder)
                return http.HttpResponse(response, mimetype='application/json')
            else:
                return render_to_response(
                    template_name,
                    data,
                    context_instance=RequestContext(request)
                )
        wrapper.__name__ = view.__name__
        wrapper.__module__ = view.__module__
        wrapper.__doc__ = view.__doc__
        return wrapper
    return decorator

"""
NOTES

To convert a model object to a dictionary but keep the related objects intact:

obj = get_object_or_404(klass, slug=slug)
fields = ['title','body']
dictionary = dict((x.name, getattr(obj, x.name)) for x in obj._meta.fields if x.name in fields)
"""