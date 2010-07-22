from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.text import truncate_html_words
from django.core.urlresolvers import reverse
from signals import *
from managers import BlogManager
import textile

class Category(models.Model):
    title       = models.CharField(max_length=250, help_text='Maximum 250 characters')
    slug        = models.SlugField(unique=True, help_text='Auto-generated, must be unique')
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['title']
    
    def __unicode__(self):
        return self.title


class Entry(models.Model):

    LIVE, DRAFT = range(1,3)
    STATUS_CHOICES = (
        (LIVE, 'Live'),
        (DRAFT, 'Draft')
    )

    # Core
    title        = models.CharField(max_length=250)
    excerpt      = models.TextField(blank=True)
    body         = models.TextField()

    # Fields to store generated HTML
    body_html    = models.TextField(editable=False, blank=True)
    excerpt_html = models.TextField(editable=False, blank=True)

    # Meta
    author          = models.ForeignKey(User)
    date_created    = models.DateTimeField(auto_now_add=True)
    date_updated    = models.DateTimeField(auto_now=True)
    enable_comments = models.BooleanField(default=True)
    slug            = models.SlugField(unique=True)
    status          = models.IntegerField(choices=STATUS_CHOICES, default=LIVE)
    featured        = models.BooleanField(default=False)

    # Categorisation
    categories = models.ManyToManyField(Category)
    # tags = TagField()


    class Meta:
        verbose_name_plural = "Entries"
        ordering = ['-date_created']

    
    def __unicode__(self):
        return self.title


    objects = BlogManager()


    def save(self, **kwargs):
        
        """ Create textile versions of the excerpt and body fields """
        
        self.body_html = textile.textile(self.body)
        if self.excerpt:
            self.excerpt_html = textile.textile(self.excerpt)
        super(Entry, self).save(**kwargs)


    def permalink(self, text=None, title=None):
        
        """ Returns an HTML link for use in the admin """
        
        if text is None:
            text = self.title
        if title is None:
            title = "Permalink to this post"
        return mark_safe('<a href="%s" rel="bookmark permalink" title="%s">%s</a>' % (self.get_absolute_url(), title, text))


    def lead_in(self):
        
        """
        Returns a truncated version of the content with an appended 'read
        more...' link
        """
        
        html = truncate_html_words(self.body, 50, end_text='')
        permalink = self.permalink(text="read more&hellip;", title="Read full article")
        return mark_safe("%s %s" % (html, permalink))

    
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

comment_was_posted.connect(comment_notifier, sender=Comment)
comment_was_posted.connect(spam_check, sender=Comment)