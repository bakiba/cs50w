from django import template
register = template.Library()
from ..models import User, Listing, Bid, Comment

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
    