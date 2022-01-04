
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("posts", views.posts, name="posts"),
    path("like/<int:post_id>", views.like, name="like"),
    path("profile/<str:user>", views.profile, name="profile"),
    path("follow/<str:user>", views.follow, name="follow"),
    path("following", views.following, name="following")
]
