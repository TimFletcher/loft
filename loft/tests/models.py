from django.contrib.auth.models import User
from django.test import TestCase
from loft.models import Entry, Category
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.test import Client
from django.core.handlers.wsgi import WSGIRequest
from django.test.client import RequestFactory

class EntryTestCase(TestCase):

    fixtures = ['users.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.superuser = User.objects.get(username='superuser')
        self.now = datetime.now()
        self.last_week = self.now - timedelta(days=7)
        self.next_week = self.now + timedelta(days=7)
        self.yesterday = self.now - timedelta(days=1)
        self.tomorrow = self.now + timedelta(days=1)

    def new_entry(self, title, body, **kwargs):
        """
        Return a new entry object
        """
        return Entry.objects.create(
            title=title,
            body=body,
            author=self.superuser,
            **kwargs
        )

    def test_live_entries(self):
        """
        Only live entries
        """
        # Not published due to (default) status
        self.new_entry("entry 1", "An entry.")
        # Published due to status
        self.new_entry("entry 2", "An entry", status=Entry.PUBLISHED)
        # Not published due to future publishing date
        self.new_entry("entry 3", "An entry", status=Entry.PUBLISHED, publish_date=self.tomorrow)
        # Published due to past publishing date
        self.new_entry("entry 4", "An entry", status=Entry.PUBLISHED, publish_date=self.yesterday)
        self.assertEquals(Entry.objects.published().count(), 2)
    
    def test_new_entry_status(self):
        """
        Default status when creating a new entry
        """
        a1 = self.new_entry("entry 1", "An entry")
        self.assertEquals(a1.status, Entry.DRAFT)

    def test_previous_entry(self):
        """
        Previous entry
        """
        a1 = self.new_entry("entry 1", "An entry", status=Entry.PUBLISHED, publish_date=self.yesterday)
        a2 = self.new_entry("entry 2", "An entry", status=Entry.PUBLISHED)
        self.assertEquals(a1, a2.get_previous_entry())

    def test_next_entry(self):
        """
        Next entry
        """
        a1 = self.new_entry("entry 1", "An entry", status=Entry.PUBLISHED, publish_date=self.yesterday)
        a2 = self.new_entry("entry 2", "An entry", status=Entry.PUBLISHED)
        self.assertEquals(a2, a1.get_next_entry())
    
    def test_create_markup(self):
        """
        Creating markup
        """
        content = "An entry"
        a1 = self.new_entry("entry 1", content, markup=Entry.MARKDOWN)
        a2 = self.new_entry("entry 2", content, markup=Entry.TEXTILE)
        self.assertEquals("<p>An entry</p>", a1.create_markup(content))
        self.assertEquals("\t<p>An entry</p>", a2.create_markup(content))

    def test_create_slug(self):
        """
        Creating slug and making sure slug can only be changed explicitly
        """
        title = "Entry 1"
        a1 = self.new_entry(title, "An entry")
        self.assertEquals("entry-1", a1.create_slug(title))
        a1.title = 'Some New Title'
        a1.save()
        self.assertEquals("entry-1", a1.slug)
        a1.slug = 'another-new-slug'
        a1.save()
        self.assertEquals('another-new-slug', a1.slug)
        
    def test_get_absolute_url(self):
        """
        Authenticated and anonymous users viewing published and draft posts
        """
        a1 = self.new_entry("Entry 1", "A published entry", status=Entry.PUBLISHED)
        a2 = self.new_entry("Entry 2", "An unpublished entry")
        
        # Anonymous user can view a published entry
        r1 = self.client.get(a1.get_absolute_url())
        self.assertEqual(r1.status_code, 200)

        # Anonymous user cannot view an unpublished entry
        r2 = self.client.get(a2.get_absolute_url())
        self.assertEqual(r2.status_code, 404)

        # Authenticated user can view an unpublished entry
        user = User.objects.create_user("user","user@example.com", "password")
        user.save()
        self.client.login(username="user", password="password")
        response = self.client.get(a2.get_absolute_url(user=user))
        self.assertEqual(response.status_code, 200)