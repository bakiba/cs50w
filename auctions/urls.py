from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create", views.create_listing_view, name="create"),
    path("listing/<int:listing_id>", views.listing_view, name="listing"),
    path("listing/<int:listing_id>/<str:action>", views.watchlist_action, name="watchlist_action"),
    path("user/<int:user_id>", views.user_listing_view, name="userlistings"),
    path("watchlist", views.watchlist_view, name="watchlist"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
