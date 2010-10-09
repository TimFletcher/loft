from django.db import models
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.comments.signals import comment_was_posted
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.text import truncate_html_words
from django.utils.translation import ugettext_lazy as _, ugettext
from django.core.urlresolvers import reverse
from managers import BlogManager
from markdown import markdown
from signals import comment_notifier, comment_spam_check
from django.template.defaultfilters import slugify
import textile

class Category(models.Model):

    name        = models.CharField(_('name'), max_length=150, db_index=True, help_text=_('Maximum 150 characters'))
    slug        = models.SlugField(_('slug'), unique=True, help_text=_('Auto-generated, must be unique'))
    description = models.CharField(_('description'), max_length=250, blank=True, help_text=_('Maximum 250 characters'))
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['name']
    
    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category, self).save(**kwargs)


class Entry(models.Model):

    LIVE, DRAFT = range(1,3)
    STATUS_CHOICES = (
        (LIVE, _('Live')),
        (DRAFT, _('Draft'))
    )
    MARKUP_CHOICES = (
        ('markdown', _('Markdown')),
        ('textile', _('Textile')),
    )

    # Core
    title        = models.CharField(_('title'), max_length=250, db_index=True)
    excerpt      = models.TextField(_('excerpt'), blank=True)
    excerpt_html = models.TextField(editable=False, blank=True)
    body         = models.TextField(_('body'), db_index=True)
    body_html    = models.TextField(editable=False, blank=True)
    # images       = models.ManyToManyField('django_snipshot.Image', related_name="entry_images")

    # Meta
    author          = models.ForeignKey(User, verbose_name=_('user'))
    created         = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)
    enable_comments = models.BooleanField(_('enable comments'), default=True)
    status          = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=LIVE)
    featured        = models.BooleanField(_('featured'), default=False)
    markup          = models.CharField(_('markup'), choices=MARKUP_CHOICES, default='textile', max_length=8)
    flattr          = models.BooleanField(default=False, help_text=_("You'll also need to manually add this article to Flattr."))
    categories      = models.ManyToManyField('loft.Category', blank=True, related_name="entry_categories", verbose_name=Category._meta.verbose_name_plural)

    # SEO
    slug              = models.SlugField(_('URL Slug'), unique=True, max_length=70)
    page_title        = models.CharField(_('Page Title'), blank=True, max_length=250, help_text="Text that appears in the tab or the top of the browser window.")
    meta_keywords     = models.CharField(_('Meta Keywords'), blank=True, max_length=250)
    meta_description  = models.CharField(_('Meta Description'), blank=True, max_length=250)
    generic_meta_tags = models.TextField(_('Generic Meta Tags'), blank=True, help_text="Code here will be added within the page's &lt;head&gt; tag.")
    
    objects = BlogManager()

    class Meta:
        verbose_name_plural = _('entries')
        ordering = ['-created']
    
    def __unicode__(self):
        return self.title

    def save(self, **kwargs):
        
        """
        Create textile OR markdown versions of the excerpt and body fields.
        Syntax highlight any code found if using Markdown.
        """

        if self.markup == 'markdown':
            self.body_html = markdown(self.body, ['codehilite'])
            if self.excerpt:
                self.excerpt_html = markdown(self.excerpt, ['codehilite'])
        elif self.markup == 'textile':
            self.body_html = textile.textile(self.body)
            if self.excerpt:
                self.excerpt_html = textile.textile(self.excerpt)
        super(Entry, self).save(**kwargs)

    def permalink(self, text=None, title=None):
        
        """ Returns an HTML link for use in the admin """
        
        if text is None:
            text = self.title
        if title is None:
            title = ugettext("Permalink to this post")
        return mark_safe('<a href="%s" rel="bookmark permalink" title="%s">%s</a>' % (self.get_absolute_url(), title, text))

    def lead_in(self):
        
        """
        Returns a truncated version of the excerpt or main content with an
        appended 'read more...' link
        
        # TODO Turn this into a template tag to allow text to be configurable?
        """
        
        if self.excerpt:
            html = self.excerpt
        else:
            html = truncate_html_words(self.body, 50, end_text='')
        permalink = self.permalink(text=ugettext("read more&hellip;"), title=ugettext("Read full article"))
        content = "%s %s" % (html, permalink)
        
        if self.markup == 'markdown':
            return mark_safe(markdown(self.excerpt, ['codehilite']))
        elif self.markup == 'textile':
            return mark_safe(textile.textile(content))
    
    def next_entry(self):
        """ Utility method to return the next published entry by date """
        return self.get_next_by_date_created(status=self.LIVE)

    def previous_entry(self):
        """ Utility method to return the previous published entry by date """
        return self.get_previous_by_date_created(status=self.LIVE)

    def get_absolute_url(self):
        if self.status == self.LIVE:
            name = 'blog_entry_detail'
            kwargs = {
                'slug': self.slug
            }
        else:
            name = 'blog_entry_draft'
            kwargs = {
                'object_id': self.id
            }
        return reverse(name, kwargs=kwargs)
    
# If we're using static-generator, blow away the cached files on save.
# TODO This needs to work for entries updated by admin actions.
if 'staticgenerator.middleware.StaticGeneratorMiddleware' in settings.MIDDLEWARE_CLASSES:
    from django.dispatch import dispatcher
    from django.db.models.signals import post_save
    from staticgenerator import quick_delete
    def delete(sender, instance, **kwargs):
        quick_delete(instance, '/')
    post_save.connect(delete, sender=Entry)

# Comment signals
comment_was_posted.connect(comment_spam_check, sender=Comment)
comment_was_posted.connect(comment_notifier, sender=Comment)