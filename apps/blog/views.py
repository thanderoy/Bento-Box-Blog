from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render
# from django.views.generic import ListView

from .models import Post


# class PostListView(ListView):
#
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'


def post_list(request):
    posts_raw = Post.published.all()

    paginator = Paginator(posts_raw, 3)
    page_number = request.GET.get('page', 1)

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If non-integer values, render first page.
        posts = paginator.page(1)
    except EmptyPage:
        # If no next page, render last page.
        posts = paginator.page(paginator.num_pages)

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
