from django.shortcuts import get_object_or_404, render

from .models import Post


def post_list(request):
    posts = Post.published.all()

    context = {'posts': posts}
    return render(request, 'blog/post/list.html', context)


def post_detail(request, id):
    post = get_object_or_404(
        Post,
        id=id,
        status=Post.Status.PUBLISHED
    )

    context = {'post': post}
    return render(request, 'blog/post/detail.html', context)
