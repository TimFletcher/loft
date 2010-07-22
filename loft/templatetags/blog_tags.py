from django import template
from loft.models import Entry
from django.template import TemplateSyntaxError

register = template.Library()

def get_latest_entries(parser, token):
    bits = token.contents.split()
    if len(bits) != 2:
        raise TemplateSyntaxError("get_latest_entries tag takes two arguments")
    return LatestEntriesNode(bits[1])
    

class LatestEntriesNode(template.Node):
    def __init__(self, num):
        self.num = num

    def render(self, context):
        context['latest_entries'] = Entry.objects.live[:self.num]
        return ''
register.tag('get_latest_entries', get_latest_entries)


def klass(ob):
    if ob.__class__.__name__ == 'Textarea':
        return 'large'
    return 'medium'
register.filter('klass', klass)