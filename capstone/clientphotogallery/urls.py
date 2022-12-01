from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import (
    index,
    GalleryCreateView,
    GalleryDetailedView,
    GalleryEditView,
    GalleryDeleteView,
    GalleryListVew,
    UserLoginView,
    UserRegisterView,
    GalleryAssetRemoveView,
    GalleryClientSelections,
    ClientLandingView,
    ClientGalleryView,
    toggleAssetSelection,
    setPrintCount,
    clientLogin,
    clientLogout,
    setClientConf,

)

urlpatterns = [
    path('', index, name='index'),
    path('dashboard/list',GalleryListVew.as_view(),name='list'),
    path('gallery/<uuid:pk>/', GalleryDetailedView.as_view(), name='detail'),
    path('gallery/create/', GalleryCreateView.as_view(), name='create'),
    path('gallery/<uuid:pk>/edit/', GalleryEditView.as_view(), name='edit'),
    path('gallery/<uuid:pk>/delete/', GalleryDeleteView.as_view(), name='delete'),
    path('gallery/<uuid:pk>/<int:id>/remove/', GalleryAssetRemoveView.as_view(), name='remove'),
    path('gallery/clientselections/', GalleryClientSelections.as_view(), name='clientselections'),
    path('dashboard/login/', UserLoginView.as_view(), name='login'),
    path('dashboard/logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('dashboard/register/', UserRegisterView.as_view(), name='register'),
    path('client/', ClientLandingView, name='clientlandingview'),
    path('client/<uuid:pk>/', ClientGalleryView, name='clientgalleryview'),
    path('api/clientlogout/', clientLogout, name='clientlogout'),
    path('api/clientlogin/<str:clientid>/', clientLogin, name='clientlogin'),
    path('api/selectasset/<int:assetid>/', toggleAssetSelection, name='selectasset'),
    path('api/setprintcount/<int:assetid>/<int:print_count>/', setPrintCount, name='setprintcount'),
    path('api/setclientconf/<str:clientid>/', setClientConf, name='setclientconf'),

]