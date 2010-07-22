from django.db import models
from datetime import datetime

class BlogManager(models.Manager):
    def _live(self):
        return self.get_query_set().filter(
            status=self.model.LIVE,
            date_created__lte=datetime.now()
        )
    live = property(_live)