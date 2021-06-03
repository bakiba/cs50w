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
    # Retrun all active listings
    listings = Listing.objects.filter(active=True).order_by("created")
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
            messages.error(request, "Invalid username and/or password.")
            return render(request, "auctions/login.html")
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
            messages.error(request, "Passwords must match.")
            return render(request, "auctions/register.html")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.error(request, "Username already taken.")
            return render(request, "auctions/register.html")
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
           messages.error(request, "Unable to save form.")
           return render(request, "auctions/create_listing.html")            
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
        if "button-comment" in request.POST:
            # we posted new comment
            comment = request.POST["comment"]
            try:
                c = Comment.objects.create(listing=listing, user=request.user, comment=comment)
                c.save()
                messages.success(request, "Comment added successfully.")
                return redirect(request.META['HTTP_REFERER'])
            except IntegrityError:
                messages.error(request, "Comment not submitted.")
                return redirect(request.META['HTTP_REFERER'])
        else:
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
        "comments" : listing.comments.all().order_by('-created')
    })

def categories_view(request):
    # Query all listings and return all distinct values from "category" field as list
    q = Listing.objects.filter(active=True).values_list('category', flat=True).distinct()
    return render(request, "auctions/categories.html", {
        "categories" : q,
        
    })

def category_view(request, category):
    # Return all listings for given category
    if category == "blank":
        q = Listing.objects.filter(active=True).filter(category='').order_by("created")
    else:
        q = Listing.objects.filter(active=True).filter(category=category).order_by("created")
    return render(request, "auctions/index.html", {
        "listings" : q,
        
    })

@login_required(login_url='login')
def user_listing_view(request, user_id):
    # Return all listings for given user   
    q = Listing.objects.filter(created_by=user_id).order_by("created")
    return render(request, "auctions/index.html", {
        "listings" : q,
        
    })
    
@login_required(login_url='login')
def listing_action(request, listing_id, action):
    # We're implementing several actions for listing:
    # add - add listing to watchlist
    # remove - remove listing from watchlist
    # close - close listing
    if action == "add":
        # Adding listing to watchlist
        l = get_object_or_404(Listing, pk=listing_id)
        try:
            # create entry in watchlist with given listing and user id
            q = Watchlist.objects.create(listing=l, user=request.user)
            q.save()
            messages.success(request, 'Listing added to watchlist.')
            return redirect(request.META['HTTP_REFERER'])
        except IntegrityError:
            messages.error(request, 'Listing already in watchlist.')
            return redirect(request.META['HTTP_REFERER'])
    elif action == "remove":
        # Removing listing from watchlist
        l = get_object_or_404(Listing, pk=listing_id)
        try:
            # retrieve the watchlist item for given user id and listing id
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
        # Retrieve all bids for the listing in descending order
        b = listing.bids.all().order_by('-bid')
        try:
            if b.exists():
                # if there were any bids, the first in the list will be the highest = winner
                listing.winner = User.objects.get(pk=b[0].user_id)
            # Deactive (close) listing
            listing.active = False
            # Update listing
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
    # Retrieve all watched listing for the user
    listings = Listing.objects.filter(watchlist__user=request.user).order_by("created")
    return render(request, "auctions/index.html", {
        "listings" : listings,
    })

@login_required(login_url='login')
def mywins_view(request):
    # Show all listings where user has won bidding
    listings = Listing.objects.filter(winner=request.user).order_by("created")
    return render(request, "auctions/index.html", {
        "listings" : listings,
    })

