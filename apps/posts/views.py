from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchQuery, \
    SearchRank, SearchVector
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response

from rest_framework.decorators import action
from .models import Post, Comment, Tag
from .serializers import CommentSerializer, PostSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.published.all()
    serializer_class = PostSerializer

    def list(self, request, tag_slug=None, query=None):
        queryset = Post.published.all()

        # Handle tag requests
        tag = None
        if tag_slug:
            tag = get_object_or_404(
                Tag,
                slug=tag_slug
            )
            queryset = queryset.filter(tags__in=[tag])

        # Handle search requests
        if query:
            search_vector = SearchVector("title", weight="A") \
                + SearchVector("body", weight="B")

            search_query = SearchQuery(query)

            queryset = queryset.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(rank__gte=0.3).order_by("-rank")

        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Post.published.all()
        post = get_object_or_404(queryset, pk=pk)

        serializer = PostSerializer(post)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def similar_posts(self, request, pk=None):
        # Get posts with tags similar to current post.
        queryset = Post.published.all()
        post = self.get_object()

        if post:
            post_tag_ids = post.tags.values_list('id', flat=True)
            print(post_tag_ids)
            queryset = queryset.filter(
                tags__in=post_tag_ids).exclude(id=post.id)
            queryset = queryset.annotate(
                same_tags=Count('tags')
                ).order_by('-same_tags', '-published_at')[:2]

        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data)

    # Latest Posts
    @action(detail=False, methods=["GET"])
    def latest_posts(self, request, *args, **kwargs):
        queryset = Post.published.all()
        count = request.query_params.get("count", 5)

        queryset = queryset.order_by("-published_at")[:int(count)]

        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data)

    # Popular Posts
    @action(detail=False, methods=["GET"])
    def popular_posts(self, request, *args, **kwargs):
        queryset = Post.published.all()
        count = request.query_params.get("count", 5)

        queryset = queryset.filter(
            comments__gt=0).annotate(
                total_comments=Count("comments")).order_by(
                    "-total_comments")[:int(count)]

        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET", "POST"], url_path="share")
    def share_via_email(self, request, pk=None, *args, **kwargs):
        """
        Endpoint to allow users share a Post via email.

        Args:
            sender (str): Name of the sender.
            receiver (str): Email of the receiver. Multiple emails can be
                provided, comma seperated.
            message (str): Message to include

        Returns:
            Response: Response object. Either 'SUCCESS' or 'ERROR' depends.
        """
        post = self.get_object()
        receiver = request.query_params.get("receiver")
        sender = request.query_params.get("sender")
        message = request.query_params.get("message")

        try:
            post.share_via_email(sender, receiver, message)
            return Response(
                {"SUCCESS": f"Post shared to {receiver}"}, status=status.HTTP_200_OK)   # noqa
        except Exception as e:
            return Response(
                {"ERROR": f"Error sending email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
