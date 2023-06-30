from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, render

from .forms import EmailPostForm
from .models import Post

SUBJECT = '[CLASSIC_BLOG] '

# from django.views.generic import ListView


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
            subject = SUBJECT + f"{data.get('name')} recommends you to read \
                { post.title}"
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
