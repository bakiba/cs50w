from ast import Delete
import os
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.files.storage import FileSystemStorage
from .storage import CustomFileSystemStorage
from django.conf import settings
# Create your models here.

class User(AbstractUser):
    pass

class Client(models.Model):
    identifier = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True)
    hideSelected = models.BooleanField(default=False)
    onlySelected = models.BooleanField(default=False)
    
    def __str__(self):
        if self.email:
            return "%s (%s)" % ( self.identifier, self.email)
        else:
            return self.identifier
    @property
    def count_selections(self):
        return self.selections.count()

class Gallery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='galleries')
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    enabled = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    password = models.CharField(max_length=25, blank=True)

    def __str__(self):
        return self.title

def upload_to_gallery(instance, filename):
    # if we're passing Asset instance, then we need access gallery.id
    if hasattr(instance, 'gallery'):
        return '{0}/{1}'.format(instance.gallery.id, filename)
    # if we're passing Gallery instance, then we need to access id
    else:
        return '{0}/{1}'.format(instance.id, filename)

class Asset(models.Model):
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name='assets')
    file = models.FileField(upload_to=upload_to_gallery, storage=CustomFileSystemStorage)

    def __str__(self):
        return self.file.name
    
    @property
    def count_selected(self):
        return self.selections.count()

    @property
    def get_comments(self):
        return self.selections.exclude(comment__exact='')
        #return Asset.objects.get(id=self.id).selections.exclude(comment__exact='').count()
    
    @property
    def get_print_count(self):
        return self.selections.aggregate(Sum('print_count'))['print_count__sum'] or 0
    
    @property
    def filename(self):
        return os.path.basename(self.file.name)

class Selection(models.Model):
    asset = models.ForeignKey(Asset,on_delete=models.CASCADE, related_name='selections' )
    client = models.ForeignKey(Client,on_delete=models.CASCADE, related_name='selections' )
    print_count = models.PositiveIntegerField(default=1)
    comment = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
       

    def serialize(self):
        return {
            "id": self.id,
            "asset": self.asset.id,
            "client": self.client.identifier,
            "coment": self.comment           
        }

@receiver(post_delete, sender=Gallery)
def gallery_post_delete_handler(sender, **kwargs):
    gallery = kwargs['instance']
    fs = FileSystemStorage()
    dir_path = os.path.join(settings.MEDIA_ROOT, str(gallery.id))

    if fs.exists(dir_path):
        files_to_remove = fs.listdir(dir_path)[1]
 
        for file in files_to_remove:
            fs.delete(os.path.join(dir_path, file))
 
        fs.delete(dir_path)

@receiver(post_delete, sender=Asset)
def gallery_post_delete_handler(sender, **kwargs):
    asset = kwargs['instance']
    storage, name = asset.file.storage, asset.file.name
    storage.delete(name)