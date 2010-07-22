from django.conf.urls.defaults import *
from models import Entry
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_detail, object_list

live_entries = {
    'queryset': Entry.objects.live.all(),
}

yearly_entries = {
    'queryset': Entry.objects.live.all(),
    'date_field': 'date_created',
    'make_object_list': True
}

urlpatterns = patterns('django.views.generic.date_based',
    url(r'^(?P<year>\d{4})/$', 'archive_year', yearly_entries, name='blog_entry_archive_year'),
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/$', 'archive_month', dict(live_entries, date_field='date_created'), name='blog_entry_archive_month'),
    (r'^comments/', include('django.contrib.comments.urls')),
)

urlpatterns += patterns('',
    url(r'^$', object_list, live_entries, name='home_index'),
    url(r'^(?P<slug>[-\w]+)/$', object_detail, live_entries, name='blog_entry_detail'),
    url(r'^draft/(?P<object_id>\d+)/$', login_required(object_detail), {'queryset': Entry.objects.all()}, name='blog_entry_draft')
)

