from rest_framework import routers

from . import views

app_name = "apps.posts"

router = routers.SimpleRouter()
router.register(r"posts", views.PostViewSet)
router.register(r"users", views.UserViewSet)
router.register(r"comments", views.CommentViewSet)

urlpatterns = router.urls
