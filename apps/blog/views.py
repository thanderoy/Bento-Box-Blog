from django.conf import settings
from django.contrib.postgres.search import (
    SearchQuery, SearchRank, SearchVector)
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from taggit.models import Tag

from .forms import CommentForm, EmailPostForm, SearchForm
from .models import Post

SUBJECT_PREFIX = '[BENTO BOX BLOG] '


def post_list(request, tag_slug=None):
    posts_raw = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(
            Tag,
            slug=tag_slug
        )
        posts_raw = posts_raw.filter(tags__in=[tag])

    paginator = Paginator(posts_raw, 5)
    page_number = request.GET.get('page', 1)

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If non-integer values, render first page.
        posts = paginator.page(1)
    except EmptyPage:
        # If no next page, render last page.
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts': posts,
        'tag': tag
    }
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
    # List of active comments
    comments = post.comments.filter(active=True)

    # Add comment Form
    form = CommentForm()

    # List of similar posts
    post_tag_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(
        tags__in=post_tag_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(
        same_tags=Count('tags')).order_by('-same_tags', '-published_at')[:2]

    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'similar_posts': similar_posts,
    }
    return render(request, 'blog/post/detail.html', context)


def post_share(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    sent = False

    if request.method == 'GET':
        form = EmailPostForm()

    elif request.method == 'POST':
        form = EmailPostForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = SUBJECT_PREFIX + f"{data.get('name')} recommends you to \
                read { post.title}"
            message = f"Read { post.title } at { post_url }\n\n \
                {data.get('name')}\'s comments: { data.get('comment')}"
            send_mail(
                subject, message, settings.EMAIL_HOST_USER, [data.get('to')]
            )
            sent = True

    context = {
        'post': post,
        'form': form,
        'sent': sent
    }
    return render(request, 'blog/post/share.html', context)


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    context = {
        'post': post,
        'form': form,
        'comment': comment
    }
    return render(request, 'blog/post/comment.html', context)


def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if "query" in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data.get("query")
            search_vector = SearchVector("title", weight="A") \
                + SearchVector("body", weight="B")

            search_query = SearchQuery(query)

            results = Post.published.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(rank__gte=0.3).order_by("-rank")

    context = {
        "form": form,
        "query": query,
        "results": results
    }

    return render(request, 'blog/post/search.html', context)
