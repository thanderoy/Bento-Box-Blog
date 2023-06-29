from django.shortcuts import get_object_or_404, render

from .models import Post


def post_list(request):
    posts = Post.published.all()

    context = {'posts': posts}
    return render(request, 'blog/post/list.html', context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        published_at__year=year,
        published_at__month=month,
        published_at__day=day,
        slug=post,

    )

    context = {'post': post}
    return render(request, 'blog/post/detail.html', context)
