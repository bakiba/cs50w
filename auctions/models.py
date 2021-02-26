from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=500)
    start_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=64, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    winner = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="wins", blank=True, null=True)

class Watchlist(models.Model):
    listing = models.ForeignKey(Listing, on_delete=CASCADE)
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="mywatch")

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="mybids")
    bid = models.DecimalField(max_digits=10, decimal_places=2)

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="mycomments")
    comment = models.CharField(max_length=500)


