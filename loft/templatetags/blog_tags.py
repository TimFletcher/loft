from django import template
from loft.models import Entry
from django.template import TemplateSyntaxError

register = template.Library()

def get_latest_entries(parser, token):
    
    """
    Add a variable to the template context containing the latest [x] blog entries.
    Default context variable is entry_list

    Syntax::

    {% get_latest_entries [limit] %}
    {% get_latest_entries [limit] as [varname] %}

    Example usage::

    {% get_latest_entries 5 %}
    {% get_latest_entries 5 as some_variable %}
    """
    
    tokens = token.contents.split()
    if len(tokens) not in (2,4):
        raise template.TemplateSyntaxError("%r tag requires 1 or 3 arguments" % tokens[0])
    if not tokens[1].isdigit():
        raise template.TemplateSyntaxError("First argument in %r tag must be an integer" % tokens[0])
    if len(tokens) == 4:
        if tokens[2] != 'as':
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'as'" % tokens[0])
        return LatestEntriesNode(tokens[1], tokens[3])
    return LatestEntriesNode(tokens[1])
register.tag('get_latest_entries', get_latest_entries)

class LatestEntriesNode(template.Node):
    def __init__(self, limit, varname=None):
        self.limit, self.varname = limit, varname

    def render(self, context):
        context[self.varname or 'entry_list'] = Entry.objects.published()[:self.limit]
        return ''