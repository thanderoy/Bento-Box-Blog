from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils import timezone

from apps.common.models import BaseModel
from taggit.managers import TaggableManager
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase


class PublishedManager(models.Manager):
    """
    Custom Manager for working with PUBLISHED posts.

    """
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')


class Post(BaseModel):

    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='published_at')
    body = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='blog_posts')
    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.DRAFT
    )
    published_at = models.DateTimeField(default=timezone.now)

    objects = models.Manager()  # Default manager.
    published = PublishedManager()  # Custom manager for PUBLISHED posts only.

    tags = TaggableManager(through=UUIDTaggedItem)

    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(
                name='reverse_published_at_index', fields=['-published_at']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'blog:post_detail',
            args=[
                self.published_at.year,
                self.published_at.month,
                self.published_at.day,
                self.slug
            ])


class Comment(BaseModel):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments'
    )
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f'Comment by {self.name} on {self.post}'
