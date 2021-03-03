from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages

from .models import User, Listing, Bid, Comment, Watchlist
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
    # We have submitted bid
    if request.method == "POST":
        bid = request.POST["bid"]
        try:
            q = Bid.objects.create(listing=listing, user=request.user, bid=bid)
            q.save()
            messages.success(request, 'Bid submitted successfully.')  
        except IntegrityError:
            messages.error(request, 'Bid not submitted.')
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
@login_required(login_url='login')
def watchlist_action(request, listing_id, action):
    if action == "add":
        l = get_object_or_404(Listing, pk=listing_id)
        try:
            q = Watchlist.objects.create(listing=l, user=request.user)
            q.save()
            messages.success(request, 'Listing added to watchlist.')
            return redirect(request.META['HTTP_REFERER'])
        except IntegrityError:
            messages.error(request, 'Listing already in watchlist.')
            return redirect(request.META['HTTP_REFERER'])
    elif action == "remove":
        #print("action remove")
        l = get_object_or_404(Listing, pk=listing_id)
        try:
            q = Watchlist.objects.get(listing=l, user=request.user)
            q.delete()
            messages.success(request, 'Listing removed from watchlist.')
            return redirect(request.META['HTTP_REFERER'])
        except IntegrityError:
            messages.error(request, 'Listing not in watchlist.')
            return redirect(request.META['HTTP_REFERER'])
    else:
        messages.error(request, 'Unknown action.')
        return redirect(request.META['HTTP_REFERER'])
    
@login_required(login_url='login')
def watchlist_view(request):
    listings = Listing.objects.filter(active=True, watchlist__user=request.user).order_by("created")
    return render(request, "auctions/index.html", {
        "listings" : listings,
    })


