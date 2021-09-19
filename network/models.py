from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import SET_NULL


class User(AbstractUser):
    following = models.ManyToManyField('self', symmetrical=False, blank=True, related_name="followers")
    
    def following_count(self):
        return self.following.count()

    def followers_count(self):
        return self.followers.count()

class Post(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='posts')
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    likes = models.ManyToManyField(User,blank=True, related_name='likes')

    def likes_count(self):
        return self.likes.count()
    
    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.get_username(),
            "title": self.title,
            "content": self.content,
            "created": self.created.strftime("%b %d %Y, %I:%M %p"),
            "likes": self.likes_count()
        }