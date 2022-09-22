from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/index.html', views.dashboard, name='dashboard'),
    path('dashboard/charts.html', views.charts, name='charts'),
    path('dashboard/tables.html', views.tables, name='tables'),
]