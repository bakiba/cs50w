import random
import json
import requests
from django.core.management.base import BaseCommand
from network.models import User, Post

class Command(BaseCommand):
    help = 'Generates some test data'
    def add_arguments(self, parser):
        parser.add_argument('-u', '--users', nargs='?', type=int, const=10, default=10, help='Indicates the number of users to be created (from 1 to n), default 10')
        parser.add_argument('-p', '--posts', nargs='?', type=int, const=50, default=50, help='Define number of posts to create, default 50')
        parser.add_argument('-l', '--likes', nargs='?', type=int, const=80, default=80, help='Define number of likes to create, default 80')
        parser.add_argument('-f', '--follows', nargs='?', type=int, const=20, default=20, help='Define number of follows to assing, default 20')

    def handle(self, *args, **kwargs):

        nusers = kwargs['users']
        nposts = kwargs['posts']
        nlikes = kwargs['likes']
        nfollows = kwargs['follows']

        # Create some users
        for i in range(1,nusers + 1):
            user = User.objects.create_user(username='test' + str(i), email='test' + str(i) + '@email.com', password='test')
            user.save()
            print(f"Created user {user.username}")
        
        all_users = User.objects.exclude(username='admin')
        
        # Generate some posts
        for _ in range(nposts):
            title = requests.get('https://baconipsum.com/api/?type=all-meat&sentences=1').json()
            content = requests.get('https://baconipsum.com/api/?type=meat-and-filler&paras=' + str(random.randint(1, 5)) + '&format=text').text
            post_user = random.choice(all_users)
            post = Post(user=post_user, title=title[0], content=content)
            post.save()
            print(f"Created post {post.id} for user {post_user.username}")
        
        
        # Assing some random likes
        for _ in range(nlikes):
            # get random post
            posts = list(Post.objects.all())
            post = random.choice(posts)

            # get random user
            user = random.choice(all_users)

            if post.user != user and post.user not in post.likes.all():
                print(f"{user.username} likes post {post.id} from {post.user}")
                post.likes.add(user)
                
        # Assing some random followers
        for _ in range(nfollows):
            user = random.choice(all_users)
            follower = random.choice(all_users)
            if user != follower and follower not in user.followers.all():
                user.followers.add(follower)
                print(f"{follower.username} folows {user.username}")
        

        

            