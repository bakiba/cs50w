import json
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator

from .models import User, Post


def index(request):
    
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@csrf_exempt

def posts(request, page=0, post_id=None):
    
    # New post must be via POST
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get('title')
        content = data.get('content')
        post = Post(user=request.user, title=title, content=content)
        post.save()
        #print(data, flush=True)
        # return all posts
        try:
            posts = Post.objects.order_by("-created").all()
            paginator = Paginator(posts, 10) # Show 25 contacts per page.    
            page_number = request.POST.get('page')
            page_obj = paginator.get_page(page_number)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)
        return JsonResponse({"pages":{"current":page_obj.number,"total":page_obj.paginator.num_pages},"posts":[post.serialize() for post in page_obj]}, safe=False)
    # else we're looking for specific post to edit
    elif request.method == "GET":
        #return JsonResponse({"message": "all ok."}, status=201)
        try:
            posts = Post.objects.order_by("-created").all()
            paginator = Paginator(posts, 10) # Show 25 contacts per page.    
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)
        return JsonResponse({"pages":{"current":page_obj.number,"total":page_obj.paginator.num_pages},"posts":[post.serialize() for post in page_obj]}, safe=False)
    else:
        return JsonResponse({
            "error": "GET or POST request required."
        }, status=400)
    
    #return render(request, "network/index.html")