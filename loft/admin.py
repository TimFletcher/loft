from django.contrib import admin
from models import Category, Entry
from django.template.defaultfilters import slugify, pluralize
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from models import Entry
from forms import CategoryAdminForm
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.urlresolvers import reverse
from django.utils.encoding import force_unicode
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.html import escape
import urllib, urllib2
import urlparse

class EntryAdmin(admin.ModelAdmin):
    
    def admin_link(self, obj):
        if obj.status == Entry.LIVE:
            text = _("View on site") + " &raquo;"
        else:
            text = _("Preview draft") + " &raquo;"
        return obj.permalink(text)
    admin_link.allow_tags = True
    admin_link.short_description = _('Link')

    def format_date(self, obj):
        return obj.publish_date.strftime('%d %b, %Y')
    format_date.short_description = _('Date Published')

    def make_published(self, request, queryset):
        row_count = queryset.update(status=Entry.LIVE)
        messages.info(request, '%d entr%s set as published.' % (row_count, pluralize(row_count, 'y was,ies were')))
    make_published.short_description = ugettext_lazy("Set selected %(verbose_name_plural)s as published")

    def make_draft(self, request, queryset):
        row_count = queryset.update(status=Entry.DRAFT)
        messages.info(request, '%d entr%s set as draft.' % (row_count, pluralize(row_count, 'y was,ies were')))
    make_draft.short_description = ugettext_lazy("Set selected %(verbose_name_plural)s as draft")

    def enable_comments(self, request, queryset):
        row_count = queryset.update(enable_comments=True)
        messages.info(request, 'Commenting was enabled on %d entr%s' % (row_count, pluralize(row_count, 'y,ies')))
    enable_comments.short_description = ugettext_lazy("Enable commenting on selected %(verbose_name_plural)s")

    def disable_comments(self, request, queryset):
        row_count = queryset.update(enable_comments=False)
        messages.info(request, 'Commenting was disabled on %d entr%s' % (row_count, pluralize(row_count, 'y,ies')))
    disable_comments.short_description = ugettext_lazy("Disable commenting on selected %(verbose_name_plural)s")
    
    list_display = ('title', 'format_date', 'status', 'enable_comments', 'admin_link')
    list_filter = ('publish_date', 'status', 'categories')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ['title']}
    ordering = ('-publish_date',)
    actions = ['make_published', 'make_draft', 'enable_comments', 'disable_comments']
    fieldsets = (
        ('Post Details', {
            'fields': ('title', 'excerpt', 'body', 'publish_date', 'status'),
        }),
        ('Metadata', {
            'fields': ('categories', 'markup', 'enable_comments', 'featured'),
            'classes': ('collapse',)
        }),
        ('Search Engine Optimisation', {
            'fields': ('slug', 'page_title', 'meta_keywords', 'meta_description', 'generic_meta_tags'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        if not obj.slug:
            obj.slug = slugify(obj.title)
        obj.save()


class CategoryAdmin(admin.ModelAdmin):

    def entry_count(self, obj):
        return obj.entry_categories.all().count()
    entry_count.short_description = _('Entries')

    form = CategoryAdminForm
    prepopulated_fields = {'slug': ['name']}
    list_display = ('name', 'description', 'entry_count')
    fieldsets = (
        ('Post Details', {
            'fields': ('name',),
        }),
        ('Metadata', {
            'fields': ('slug', 'description'),
        }),
    )

        
admin.site.register(Entry, EntryAdmin)
admin.site.register(Category, CategoryAdmin)