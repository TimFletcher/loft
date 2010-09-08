from django.contrib import admin
from models import Category, Entry
from django.template.defaultfilters import slugify, pluralize
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from models import Entry
from forms import CategoryAdminForm

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
        return obj.date_created.strftime('%d %b, %Y')
    format_date.short_description = _('Date Created')

    def make_published(self, request, queryset):
        row_count = queryset.update(status=Entry.LIVE)
        if row_count == 1:
            snippet = "entry was"
        else:
            snippet = "entries were"
        messages.info(request, '%d %s set as published.' % (row_count, snippet))
    make_published.short_description = ugettext_lazy("Set selected %(verbose_name_plural)s as published")

    def make_draft(self, request, queryset):
        row_count = queryset.update(status=Entry.DRAFT)
        if row_count == 1:
            snippet = "entry was"
        else:
            snippet = "entries were"
        messages.info(request, '%d %s set as draft.' % (row_count, snippet))
    make_draft.short_description = ugettext_lazy("Set selected %(verbose_name_plural)s as draft")

    list_display = ('title', 'format_date', 'status', 'admin_link')
    list_filter = ('date_created', 'status', 'categories')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ['title']}
    ordering = ('-date_created',)
    actions = ['make_published', 'make_draft']
    
    fieldsets = (
        ('Post Details', {
            'fields': ('title', 'excerpt', 'body', 'categories'),
        }),
        ('Metadata', {
            'fields': ('enable_comments', 'slug', 'status', 'markup', 'featured', 'flattr')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
            obj.slug   = slugify(obj.title)
        obj.save()


class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    prepopulated_fields = {'slug': ['name']}
    list_display = ('name', 'description')
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