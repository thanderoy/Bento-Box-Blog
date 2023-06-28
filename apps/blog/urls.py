from django.urls import path
from . import views


app_name = 'apps.blog'


urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('<uuid:id>/', views.post_detail, name='post_detail'),
]
