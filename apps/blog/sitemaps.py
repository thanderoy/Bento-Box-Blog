from django.contrib.sitemaps import Sitemap
from django.db.models.base import Model

from .models import Post


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Post.published.all()

    def lastmod(self, obj: Model) -> str:
        return obj.updated_at
