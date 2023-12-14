from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic.base import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, \
    SpectacularSwaggerView

from apps.posts.sitemaps import PostSitemap

sitemaps = {
    "posts": PostSitemap,
}

urlpatterns = [
    path("bundus/", admin.site.urls),
    path("", include("apps.posts.urls", namespace="posts")),
    path(
        "sitemap.xml", sitemap, {"sitemaps": sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
    path('', RedirectView.as_view(url='/posts/', permanent=True)),
]

# Django Silk + Swagger Docs
urlpatterns += [
    path('silk/', include('silk.urls', namespace='silk')),
    path('api/docs/', SpectacularAPIView.as_view(), name='docs'),
    path('api/docs/swagger-ui/', SpectacularSwaggerView.as_view(url_name='docs'), name='swagger-ui'),   # noqa
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='docs'), name='redoc'),   # noqa
]
