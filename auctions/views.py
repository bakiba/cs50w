from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import User, Listing, Bid, Comment
from .forms import ListingForm

from django import template
register = template.Library()

def index(request):
    listings = Listing.objects.filter(active=True).order_by("created")
    '''
    for listing in listings:
        bids = listing.bids.all()
        if (bids.values().count()):
            max_bid = listing.bids.all().values().order_by('-bid')[0]
            print(max_bid['bid'])
            #listing.start_bid = max_bid['bid']
            #print(list(listing))
    '''
    return render(request, "auctions/index.html", {
        "listings" : listings,
    })


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url='login')
def create_listing_view(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.created_by_id = request.user.id
            entry.save()
            return HttpResponseRedirect(reverse("index"))
        else:
           return render(request, "auctions/create_listing.html", {
                "message": "Unable to save form.",
                "form":form
            }) 

            
    else:
        return render(request,"auctions/create_listing.html", {
            "form": ListingForm()
        })

def listing_view(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)   
    #listing = Listing.objects.get(pk=listing_id)
    '''
    bids = listing.bids.all()
    if (bids.values().count()):
        bids = listing.bids.all().values().order_by('-bid')
    '''
    return render(request, "auctions/view_listing.html", {
        "listing" : listing,
     #   "bids" : bids,
    })

@login_required(login_url='login')
def user_listing_view(request, user_id):
    #listing = get_object_or_404(Listing, pk=listing_id)   
    q = Listing.objects.filter(active=True, created_by=user_id).order_by("created")
    
    return render(request, "auctions/index.html", {
        "listings" : q,
        
    })


