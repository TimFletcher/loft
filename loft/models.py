from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.comments.signals import comment_was_posted, comment_will_be_posted
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.text import truncate_html_words
from django.utils.translation import ugettext_lazy as _, ugettext
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django import http
from markdown import markdown
from signals import comment_notifier, comment_spam_check
from datetime import datetime
import textile


class BlogManager(models.Manager):

    def published(self):
        return self.filter(
            Q(publish_date__lte=datetime.now()) | Q(publish_date__isnull=True),
            status=self.model.PUBLISHED
        )


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

    PUBLISHED, DRAFT = range(1,3)
    STATUS_CHOICES = (
        (PUBLISHED, _('Published')),
        (DRAFT, _('Draft'))
    )
    MARKDOWN, TEXTILE = range(1,3)
    MARKUP_CHOICES = (
        (MARKDOWN, _('Markdown')),
        (TEXTILE, _('Textile')),
    )
    
    MARKUP_HELP = _("""Select the type of markup you are using in this entry.<br/>
<a href="http://daringfireball.net/projects/markdown/basics" target="_blank">Markdown Guide</a> - 
<a href="http://thresholdstate.com/articles/4312/the-textile-reference-manual" target="_blank">Textile Guide</a>""")

    # Core
    title        = models.CharField(_('title'), max_length=250, db_index=True)
    excerpt      = models.TextField(_('excerpt'), blank=True)
    excerpt_html = models.TextField(editable=False, blank=True)
    body         = models.TextField(_('body'), db_index=True)
    body_html    = models.TextField(editable=False, blank=True)

    # Meta
    author          = models.ForeignKey(User, verbose_name=_('user'))
    publish_date    = models.DateTimeField(blank=True, null=True, help_text=_("Only set this if you want your article to be published on a future date."))
    enable_comments = models.BooleanField(_('enable comments'), default=True)
    status          = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=DRAFT)
    featured        = models.BooleanField(_('featured'), default=False)
    markup          = models.IntegerField(_('markup'), choices=MARKUP_CHOICES, default=MARKDOWN, help_text=MARKUP_HELP)
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
        ordering = ['-publish_date']
    
    def __unicode__(self):
        return self.title

    def save(self, **kwargs):
        self.body_html = self.create_markup(self.body)
        if self.excerpt:
            self.excerpt_html = self.create_markup(self.excerpt)

        # If the entry doesn't have a slug the first time it's saved, add one
        if not self.id:
            if not self.slug:
                self.slug = self.create_slug(self.title)
            if not self.publish_date:
                self.publish_date = datetime.now()
        super(Entry, self).save(**kwargs)

    def create_markup(self, content):
        """
        Create textile OR markdown versions of the excerpt and body fields.
        Syntax highlight any code found if using Markdown.
        """
        if self.markup == Entry.MARKDOWN:
            return markdown(content, ['codehilite'])
        elif self.markup == Entry.TEXTILE:
            return textile.textile(content)
        else:
            return content

    def create_slug(self, title):
        return slugify(title)

    def permalink(self, text=None, title=None):
        """
        Returns an HTML link for use in the admin
        """
        if text is None: text = self.title
        if title is None: title = ugettext("Permalink to this post")
        return mark_safe('<a href="%s" rel="bookmark permalink" title="%s">%s</a>' % (self.get_absolute_url(), title, text))

    def lead_in(self):
        """
        Returns a truncated version of the excerpt or main content with an
        appended 'read more...' link
        """
        if self.excerpt:
            html = self.excerpt
        else:
            html = truncate_html_words(self.body, 50, end_text='')
        permalink = self.permalink(text=ugettext("read more&hellip;"), title=ugettext("Read full article"))
        content = "%s %s" % (html, permalink)

        if self.markup == Entry.MARKDOWN:
            return mark_safe(markdown(self.excerpt, ['codehilite']))
        elif self.markup == Entry.TEXTILE:
            return mark_safe(textile.textile(content))

    def get_previous_entry(self):
        """
        Utility method to return the previous published entry
        """
        qs = Entry.objects.published().exclude(pk=self.pk)
        try:
            return qs.filter(publish_date__lte=self.publish_date).order_by('publish_date')[0]
        except IndexError, e:
            return None

    def get_next_entry(self):
        """
        Utility method to return the next published entry
        """
        qs = Entry.objects.published().exclude(pk=self.pk)
        try:
            return qs.filter(publish_date__gte=self.publish_date).order_by('-publish_date')[0]
        except IndexError, e:
            return None

    def is_draft(self):
        return self.status == self.DRAFT

    def is_published(self):
        return self.status == self.PUBLISHED

    def get_absolute_url(self, user=None):
        """
        Return a url based on the publication status of the object. Access
        control of these urls should be done in their views or the URL conf.
        """
        if self.status == self.PUBLISHED:
            name = 'blog_entry_detail'
            kwargs = {'slug': self.slug}
        else:
            name = 'blog_entry_draft'
            kwargs = {'object_id': self.id}
        return reverse(name, kwargs=kwargs)
    
# If we're using static-generator, blow away the cached files on save.
if 'staticgenerator.middleware.StaticGeneratorMiddleware' in settings.MIDDLEWARE_CLASSES:
    from django.dispatch import dispatcher
    from django.db.models.signals import post_save
    from staticgenerator import quick_delete
    def delete(sender, instance, **kwargs):
        quick_delete(instance, '/')
    post_save.connect(delete, sender=Entry)

# Comment signals
comment_will_be_posted.connect(comment_spam_check, sender=Comment)
comment_was_posted.connect(comment_notifier, sender=Comment)