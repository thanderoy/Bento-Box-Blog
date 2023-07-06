import markdown
from django.contrib.syndication.views import Feed
from django.db.models import QuerySet
from django.db.models.base import Model
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy

from .models import Post


class LatestPostsFeed(Feed):
    title = "Bento Box Blog"
    link = reverse_lazy("blog:post_list")
    description = "New on Bento Box Blog"

    def items(self) -> QuerySet:
        return Post.published.all()[:5]

    def item_title(self, item: Model) -> str:
        return item.title

    def item_description(self, item: Model) -> str:
        return truncatewords_html(markdown.markdown(item.body), 30)

    def item_pubdate(self, item: Model) -> str:
        return item.published_at
