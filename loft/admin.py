from django.contrib import admin
from models import Category, Entry
from django.template.defaultfilters import slugify

class EntryAdmin(admin.ModelAdmin):
    
    def admin_link(self, obj):
        if obj.status == Entry.LIVE:
            text = "View on site &raquo;"
        else:
            text = "Preview draft &raquo;"
        return obj.permalink(text)

    admin_link.allow_tags = True
    admin_link.short_description = 'Link'

    def format_date(self, obj):        
        return obj.date_created.strftime('%d %b, %Y')
    format_date.short_description = 'Date Created'
    
    list_display = ('title', 'format_date', 'status', 'admin_link')
    list_filter = ('date_created', 'status')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ['title']}
    ordering = ('-date_created',)

    actions_selection_counter = True
    
    fieldsets = (
        ('Post Details', {
            'fields': ('title', 'excerpt', 'body'),
        }),
        ('Metadata', {
            'fields': ('enable_comments', 'slug', 'status', 'featured')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
            obj.slug   = slugify(obj.title)
        obj.save()
    
admin.site.register(Entry, EntryAdmin)