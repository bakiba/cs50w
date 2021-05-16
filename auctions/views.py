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
    # We've submitted the create listing form
    if request.method == "POST":
        form = ListingForm(request.POST)
        # if form is valid
        if form.is_valid():
            # Save form data into variable but do not commit to DB
            entry = form.save(commit=False)
            # We need to add current user to the fields
            entry.created_by_id = request.user.id
            # and finaly send data to DB
            entry.save()
            return HttpResponseRedirect(reverse("index"))
        else:
           # if form is not valid, return data to user
           return render(request, "auctions/create_listing.html", {
                "message": "Unable to save form.",
                "form":form
            })            
    else:
        # present the create listing form
        return render(request,"auctions/create_listing.html", {
            "form": ListingForm()
        })

def listing_view(request, listing_id):
    # First retrieve lising from DB
    listing = get_object_or_404(Listing, pk=listing_id)
    # We have submitted bid
    if request.method == "POST":
        # get the submitted bid
        bid = request.POST["bid"]
        try:
            # Save the bid into DB. We're not doing much checking here, relaying on form validation logic
            q = Bid.objects.create(listing=listing, user=request.user, bid=bid)
            q.save()
            messages.success(request, 'Bid submitted successfully.') 
            # Return to the same page with cleared POST
            return redirect(request.META['HTTP_REFERER'])
        except IntegrityError:
            messages.error(request, 'Bid not submitted.')
            return redirect(request.META['HTTP_REFERER'])
    # Retrieve all bids for given listing ordered from highest to lowest
    b = listing.bids.all().order_by('-bid')
    # determine if current user is:
    #   bidding: curent user id will be in queryset 
    #   winning: user id of the first bid in list == current user id
    #   not winning: user id of the first bid != current user id
    if(b.filter(user_id=request.user.id)):
        if (b[0].user_id == request.user.id):
            win = "winning"
        else:
            win = "not winning"
    else:
        win = "not bidding"
    
    # render the view 
    return render(request, "auctions/view_listing.html", {
        "listing" : listing,
        "win" : win,
    })

def categories_view(request):
    q = Listing.objects.filter(active=True).values_list('category', flat=True).distinct()
    return render(request, "auctions/categories.html", {
        "categories" : q,
        
    })
def category_view(request, category):
    if category == "blank":
        q = Listing.objects.filter(active=True).filter(category='').order_by("created")
    else:
        q = Listing.objects.filter(active=True).filter(category=category).order_by("created")
    return render(request, "auctions/index.html", {
        "listings" : q,
        
    })
@login_required(login_url='login')
def user_listing_view(request, user_id):
    #listing = get_object_or_404(Listing, pk=listing_id)   
    q = Listing.objects.filter(created_by=user_id).order_by("created")
    return render(request, "auctions/index.html", {
        "listings" : q,
        
    })
    
@login_required(login_url='login')
def listing_action(request, listing_id, action):
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
    elif action == "close":
        # once bid is closed update winner and also remove entry from watchlist for all users who were watching
        listing = get_object_or_404(Listing, pk=listing_id)
        b = listing.bids.all().order_by('-bid')
        try:
            if b.exists():
                listing.winner = User.objects.get(pk=b[0].user_id)
            listing.active = False
            listing.save()
            messages.success(request, 'Listing successfully closed.')
            return redirect(request.META['HTTP_REFERER'])
        except IntegrityError:
            messages.error(request, 'Unable to close listing.')
            return redirect(request.META['HTTP_REFERER'])
    else:
        messages.error(request, 'Unknown action.')
        return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login')
def watchlist_view(request):
    listings = Listing.objects.filter(watchlist__user=request.user).order_by("created")
    return render(request, "auctions/index.html", {
        "listings" : listings,
    })
@login_required(login_url='login')
def mywins_view(request):
    listings = Listing.objects.filter(winner=request.user).order_by("created")
    return render(request, "auctions/index.html", {
        "listings" : listings,
    })

