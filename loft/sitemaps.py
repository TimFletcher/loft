from django.contrib.sitemaps import Sitemap
from models import Entry

class LoftSitemap(Sitemap):
    changefreq = "never"
    priority = 0.8

    def items(self):
        return Entry.objects.published()

    def lastmod(self, obj):
        return obj.updated