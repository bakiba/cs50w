import json
from django.http import JsonResponse, request
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
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
def posts(request, page=0, post_id=None, profile=None):
    
    # if user is not logged, then we do not need user like list
    if request.user.is_authenticated:
        likes = User.objects.get(pk=request.user.id).likes.all()
    else:
        likes = []
    # New post must be via POST
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get('title')
        content = data.get('content')
        post = Post(user=request.user, title=title, content=content)
        post.save()
    # if profile parameter is set
    profile = request.POST.get('profile', request.GET.get('profile'))
    # if profile is given, return only posts for that user
    if profile != None and profile != 'undefined' and profile != 'null':
        posts = Post.objects.filter(user__username=profile).order_by("-created").all()
    # return all posts from newest to oldest
    else:
        posts = Post.objects.order_by("-created").all()
    # Show 25 contacts per page.
    paginator = Paginator(posts, 10) 
    # if page was set via post or get, jump to that page
    page_number = request.POST.get('page', request.GET.get('page'))
    page_obj = paginator.get_page(page_number)
    return JsonResponse({"pages":{"current":page_obj.number,"total":page_obj.paginator.num_pages},"posts":[post.serialize() for post in page_obj],"likes":[post.id for post in likes]}, safe=False)
"""         try:
            posts = Post.objects.order_by("-created").all()
            paginator = Paginator(posts, 10) # Show 25 contacts per page.    
            page_number = request.POST.get('page')
            page_obj = paginator.get_page(page_number)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)
        return JsonResponse({"pages":{"current":page_obj.number,"total":page_obj.paginator.num_pages},"posts":[post.serialize() for post in page_obj],"likes":[post.id for post in likes]}, safe=False)
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
        return JsonResponse({"pages":{"current":page_obj.number,"total":page_obj.paginator.num_pages},"posts":[post.serialize() for post in page_obj],"likes":[post.id for post in likes]}, safe=False)
    else:
        return JsonResponse({
            "error": "GET or POST request required."
        }, status=400) """

@csrf_exempt
@login_required(login_url='login')
def like(request, post_id):
    if request.user.is_authenticated == None:
        return JsonResponse({"error": "User must login to like."}, status=404)   
    if request.method == "PUT":
        # Query for requested post 
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)    
        if (post.user == request.user):
            #Can't like own post
            return JsonResponse({"likeBtnTxt":"Like", "likes":post.likes_count()})
        if (request.user in post.likes.all()):
            #Unlike the post
            post.likes.remove(request.user)
            #Set button back to "Like" so we can like it again
            return JsonResponse({"likeBtnTxt":"Like", "likes":post.likes_count()})
        #Like post
        post.likes.add(request.user)
        return JsonResponse({"likeBtnTxt":"Unlike", "likes":post.likes_count()}) 
    

def profile(request, user):
    # get the user object
    profile = User.objects.get(username=user)
    following = list(user.username for user in profile.following.all())
    followers = list(user.username for user in profile.followers.all())

    return render(request, "network/profile.html", {
        "profile":profile.username,
        "following":following, 
        "followers":followers
    })


@login_required(login_url='login')
def follow(request, user):
    if request.user.is_authenticated == None:
        return redirect(request.META['HTTP_REFERER'])  
    # Query for requested post 
    try:
        profile = User.objects.get(username=user)
    except User.DoesNotExist:
        return redirect(request.META['HTTP_REFERER'])     
    if (profile.username == request.user):
        #Can't follow self
        return redirect(request.META['HTTP_REFERER']) 
    if (request.user in profile.followers.all()):
        #Unfollow the user
        profile.followers.remove(request.user)
        #Set button back to "Follow" so we can follow user again
        return redirect(request.META['HTTP_REFERER']) 
    #Follow the user
    profile.followers.add(request.user)
    return redirect(request.META['HTTP_REFERER'])  