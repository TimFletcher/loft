from django.contrib.auth.models import User
from django.test import TestCase
from loft.models import Entry, Category
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.test import Client
from django.core.handlers.wsgi import WSGIRequest
from django.test.client import RequestFactory

class ViewTestCase(TestCase):

    fixtures = ['users.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.superuser = User.objects.get(username='superuser')
        self.anonymous = User.objects.get(username='anonymous')
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

    def test_blog_index(self):
        """
        Only live entries
        """
        # Not published due to default status (status=Entry.DRAFT)
        e1 = self.new_entry("entry 1", "An entry.")
        # Published due to status
        e2 = self.new_entry("entry 2", "An entry", status=Entry.PUBLISHED)
        # Not published due to future publishing date
        e3 = self.new_entry("entry 3", "An entry", status=Entry.PUBLISHED, publish_date=self.tomorrow)
        # Published due to past publishing date
        e4 = self.new_entry("entry 4", "An entry", status=Entry.PUBLISHED, publish_date=self.yesterday)
        
        r1 = self.client.get(reverse('blog_index'))
        self.assertEquals(r1.status_code, 200)
        self.assertEquals(str(r1.context['object_list']), str([e2, e4]))