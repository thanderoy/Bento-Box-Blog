from unittest import mock

from django.conf import settings
from django.test import TestCase
from model_bakery import baker

from apps.posts.models import Post


class TestPublishedManager(TestCase):

    def setUp(self) -> None:
        self.draft_posts = baker.make(
            Post, status=Post.Status.DRAFT, _quantity=3)
        self.published_posts = baker.make(
            Post, status=Post.Status.PUBLISHED, _quantity=4)

        return super().setUp()

    def test_get_queryset(self):
        # Get only 'PUBLISHED' Posts
        queryset = Post.published.all()
        assert set(queryset) == set(self.published_posts)
        assert queryset.count() == 4

        # Get all Posts
        queryset = Post.objects.all()
        assert set(queryset) == set(self.published_posts + self.draft_posts)
        assert queryset.count() == 7


class TestPost(TestCase):

    def setUp(self) -> None:
        self.post = baker.make(Post, title="Great Title")

        return super().setUp()

    @mock.patch("apps.posts.models.send_mail")
    def test_share_via_email(self, mock_send_mail):
        self.post.share_via_email(
            'Nico', 'receiver@example.com', 'Check out this post'
        )

        subject = f"{settings.SUBJECT_PREFIX} Nico recommends you to read Great Title"  # noqa
        message = f"Read Great Title at {self.post.get_absolute_url()}\n Nico's comments: Check out this post"  # noqa

        mock_send_mail.assert_called_once_with(
            subject, message, settings.EMAIL_HOST_USER, ['receiver@example.com']
        )
