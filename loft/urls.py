from django.conf.urls.defaults import *
from django.contrib.auth.decorators import user_passes_test
from models import Entry
from django.views.generic.list_detail import object_detail, object_list
from feeds import LoftEntryFeedRSS, LoftEntryFeedAtom
import views as loft_views

draft_detail_view = user_passes_test(lambda u: u.is_staff)(object_detail)

live_entries = {
    'queryset': Entry.objects.published(),
}

monthly_entries = dict(live_entries.items() + [
    ('date_field', 'created')
])

yearly_entries = dict(monthly_entries.items() + [
    ('date_field', 'created'),
    ('make_object_list', True)
])


urlpatterns = patterns('',
    url(r'^$', loft_views.list, {'klass': Entry}, name='blog_index'),
    url(r'^(?P<slug>[-\w]+)/$', loft_views.detail, {'klass': Entry}, name='blog_entry_detail'),
    url(r'^draft/(?P<object_id>\d+)/$', draft_detail_view, {'queryset': Entry.objects.all()}, name='blog_entry_draft'),
    url(r'^feeds/rss/$', LoftEntryFeedRSS(), name='blog_rss_feed'),
    url(r'^feeds/atom/$', LoftEntryFeedAtom(), name='blog_atom_feed')
)

urlpatterns += patterns('django.views.generic.date_based',
    url(r'^(?P<year>\d{4})/$', 'archive_year', yearly_entries, name='blog_entry_archive_year'),
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/$', 'archive_month', monthly_entries, name='blog_entry_archive_month'),
    (r'^comments/', include('django.contrib.comments.urls')),
)
