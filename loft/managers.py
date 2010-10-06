from django.db import models
from datetime import datetime

class BlogManager(models.Manager):

    def published(self):
        return self.exclude(
            status=self.model.DRAFT,
            created__lte=datetime.now
        )