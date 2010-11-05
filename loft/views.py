from models import Entry
from decorators import add_ajax

@add_ajax('loft/entry_detail.html')
def detail(request, klass, slug):
    obj_list = klass._default_manager.all()
    obj = obj_list.filter(slug=slug)
    return {
        'object_list': obj_list,
        'object_list_json': obj_list.values('title', 'created'),
        'object': obj[0],
        'object_json': obj.values('title', 'created')[0]
    }