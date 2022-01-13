from django.core.management.base import BaseCommand
from network.models import User, Post

class Command(BaseCommand):
    help = 'Delete all test data'

    def handle(self, *args, **kwargs):
        
        # Delete all data (exept admin user)
        User.objects.exclude(username='admin').delete()
        Post.objects.all().delete()
        

            