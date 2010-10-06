from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from models import Entry

class LoftEntryFeedRSS(Feed):
    title = "Timothy Fletcher's Blog Feed"
    link = "/"
    description = "A web developer's blog."

    def items(self):
        return Entry.objects.published()[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt_html

class LoftEntryFeedAtom(LoftEntryFeedRSS):
    feed_type = Atom1Feed