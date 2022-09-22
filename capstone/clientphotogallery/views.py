from django.http import HttpResponse
from django.shortcuts import render, redirect

def index(request):
    #return HttpResponse("Hello, world!")
    return render(request, "clientphotogallery/index.html")

def dashboard(request):
    #return HttpResponse("Hello, world!")
    return render(request, "clientphotogallery/dashboard.html")

def charts(request):
    return render(request, "clientphotogallery/charts.html")

def tables(request):
    return render(request, "clientphotogallery/tables.html")