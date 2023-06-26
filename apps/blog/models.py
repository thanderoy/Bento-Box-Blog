from apps.common.models import BaseModel
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Add Blog Models : Add Post Model, Add datetime fields,
#   Add default sort order, Add DB Index at `published_at` field


class Post(BaseModel):

    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250)
    body = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='blog_posts')
    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.DRAFT
    )
    published_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(
                name='reverse_published_at_index', fields=['-published_at']),
        ]

    def __str__(self):
        return self.title
