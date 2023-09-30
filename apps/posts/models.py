from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.core.mail import send_mail
from django.conf import settings

from apps.common.models import BaseModel


class PublishedManager(models.Manager):
    """
    Custom Manager for working with PUBLISHED posts.

    """
    def get_queryset(self):
        """
        Custom get_queryset method. Add some abstraction for 'DRAFT' posts.

        Returns:
            queryset: Queryset object with 'PUBLISHED' posts.
        """
        return super().get_queryset().filter(
            status=Post.Status.PUBLISHED)


class Tag(BaseModel):
    name = models.CharField(max_length=20)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


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
    is_deleted = models.BooleanField(default=False)

    objects = models.Manager()  # Default manager.
    published = PublishedManager()  # Custom manager for PUBLISHED posts only.

    tags = models.ManyToManyField(Tag, blank=True)

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
            'posts:post-detail',
            args=[self.slug]
            )

    def share_via_email(self, sender=None, receiver=None, message=None):
        if sender and receiver:
            post_url = self.get_absolute_url()
            subject = f"{settings.SUBJECT_PREFIX} {str(sender)} recommends you to read { self.title}"  # noqa
            message = f"Read { self.title } at { post_url }\n {str(sender)}\'s comments: {message}" # noqa
            receipients = []
            if receiver:
                receipients.append(receiver)

            try:
                send_mail(
                    subject, message, settings.EMAIL_HOST_USER,
                    receipients
                )
                return True
            except Exception as e:
                print({"ERROR": f"Error sending email: {str(e)}"},)
                return False

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)


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
