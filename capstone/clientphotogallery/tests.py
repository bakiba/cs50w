import random
import os
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import FileSystemStorage
from django.test import Client, TestCase
from .models import User, Client, Asset, Gallery, Selection
from django.urls import reverse

# NOTE: when runing tests, make sure to set up SECRET_KEY in the settings.py. Unittest does not load environmat variable.

# Create your tests here.
numClients = 5
numAssets = 50
numSelections = 100

class ModelTestCase(TestCase):
      
    def setUp(self):
        # Photographers
        p1 = User.objects.create(username="photographer1", password="password1")
        p2 = User.objects.create(username="photographer2", password="password2")

        # Create galleries
        g1 = Gallery.objects.create(owner=p1, title="Gallery 1", description="Photographer 1 gallery enabled no password", enabled=True)
        g2 = Gallery.objects.create(owner=p1, title="Gallery 2", description="Photographer 1 gallery enabled with password", enabled=True, password="1234")
        g3 = Gallery.objects.create(owner=p2, title="Gallery 3", description="Photographer 2 gallery not enabled with password", password="1234")
        g3 = Gallery.objects.create(owner=p2, title="Gallery 4", description="Photographer 2 gallery archived no password", archived=True)

        # Add clients     
        for i in range(1, numClients + 1):
            Client.objects.create(identifier="client" + str(i))

        # set-up assets
        galleries = Gallery.objects.all()
        for i in range(1, numAssets + 1):
            file = SimpleUploadedFile(name='test_image' + str(i) + '.jpg' , content=b'', content_type='image/jpeg')
            Asset.objects.create(gallery=random.choice(galleries), file=file)
        
        # Add selections
        clients = Client.objects.all()
        assets = Asset.objects.all()
        for i in range(1, numSelections + 1):
            Selection.objects.create(asset=random.choice(assets), client=random.choice(clients), print_count=random.randint(1, 5))


    def tearDown(self):
        # We need to delete the files created in the media folder
        galleries = Gallery.objects.all()
        fs = FileSystemStorage()
        for gallery in galleries:
            dir_path = os.path.join(settings.MEDIA_ROOT, str(gallery.id))
            if fs.exists(dir_path):
                gallery.delete()
                fs.delete(dir_path)

    def test_photographer_count(self):
        p = User.objects.all()
        self.assertEqual(p.count(), 2)
        
    def test_client_count(self):
        c = Client.objects.all()
        self.assertEqual(c.count(), numClients)

    def test_asset_count(self):
        a = Asset.objects.all()
        self.assertEqual(a.count(), numAssets)

    def test_selection_count(self):
        s = Selection.objects.all()
        print(f"There are total {s.count()} selections")
        self.assertEqual(s.count(), numSelections)

    def test_selection_print_count(self):
        s = Selection.objects.filter(print_count__gte=3)
        print(f"There are {s.count()} selections with print_count >= 3")
        self.assertGreaterEqual(s.count(), 1)
    
    def test_selection_client(self):
        clients = Client.objects.all()
        s = Selection.objects.filter(client=random.choice(clients))
        print(f"There are {s.count()} selections for {s[0].client}")
        self.assertGreaterEqual(s.count(), 1)

    def test_verify_file_count(self):
        galleries = Gallery.objects.all()     
        fs = FileSystemStorage()
        for gallery in galleries:
            file_count = gallery.assets.count()
            dir_path = os.path.join(settings.MEDIA_ROOT, str(gallery.id))
            if fs.exists(dir_path):
                files_in_gallery = len(fs.listdir(dir_path)[1])
                print(f"Gallery {gallery.title} has {file_count} assets and there was {files_in_gallery} files fond on the filesystem")
                self.assertEqual(file_count, files_in_gallery)
    
    def test_login_redirect(self):
        response = self.client.get(reverse('list'))
        self.assertRedirects(response, '/dashboard/login/?next=/dashboard/list')

    def test_gallery_list_view(self):
        login = self.client.force_login(User.objects.get(username='photographer1'))
        response = self.client.get(reverse('list'))
        # verify status_code 200
        self.assertEqual(response.status_code, 200)
        # verify login user
        self.assertEqual(str(response.context['user']), 'photographer1')
        # verify correct template
        self.assertTemplateUsed(response, 'clientphotogallery/dashboard.html')
        # verify number of selections in view match the number of selections in db
        owner = User.objects.get(username=str(response.context['user']))
        client = random.choice(Client.objects.all())
        s = Selection.objects.filter(asset__gallery__owner=owner, client__identifier=client)
        view_selections = response.context['selections']
        client1_count = 0
        for vselection in view_selections:
            if vselection['client__identifier'] == client.identifier:
                client1_count += 1
        print(f"{owner.username} has {s.count()} selections in db and {client1_count} in view made by {client.identifier}")
        self.assertEqual(s.count(), client1_count)
        

