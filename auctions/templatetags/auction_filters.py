from django import template
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from decimal import Decimal

register = template.Library()
from ..models import User, Listing, Bid, Comment, Watchlist

@register.filter
def price(value):
    #print("listing id:", value)
    listing = Listing.objects.get(pk=value)
    bids = listing.bids.all()
    if (bids.values().count()):
       max_bid = listing.bids.all().values().order_by('-bid')[0]
       return max_bid['bid']
    else:
        return listing.start_bid

@register.filter
def bid_count(value):
    #print("listing id:", value)
    listing = Listing.objects.get(pk=value)
    bids = listing.bids.all()
    return bids.values().count()

@register.filter
def comment_count(value):
    #print("listing id:", value)
    listing = Listing.objects.get(pk=value)
    comments = listing.comments.all()
    return comments.values().count()  

@register.filter
def watch_count(value):
    #print("listing id:", value)
    return Listing.objects.filter(watchlist__user=value).count()
    
@register.simple_tag
def is_watched(listing_id, user_id):
    #print("listing id:", listing_id)
    l = Listing.objects.get(pk=listing_id)
    u = User.objects.get(pk=user_id)
    return Watchlist.objects.filter(listing=l, user=u).exists() 

@register.filter
def min_bid(value):
    #print("listing id:", value)
    return round(Decimal(value) + Decimal(0.1),2)
#https://hunj.dev/blog/python-validate-url/
@register.filter
def valid_url(to_validate):
    validator = URLValidator()
    try:
        validator(to_validate)
        # url is valid here
        # do something, such as:
        return True
    except ValidationError as exception:
        # URL is NOT valid here.
        # handle exception..
        #print(exception)
        return False 
    