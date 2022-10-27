from multiprocessing import context
import re, uuid, json
from xml.dom.minidom import Identified
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied, ValidationError
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.views import LoginView

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import User, Client, Gallery, Asset, Selection, upload_to_gallery
from django.db.models import Count
from django.db import transaction
from .forms import GalleryCreateForm, GalleryEditForm, RegisterForm
from django import forms
from django.http import HttpResponse, JsonResponse


def index(request):
    #return HttpResponse("Hello, world!")
    return render(request, "clientphotogallery/index.html")

def dashboard(request):
    #return HttpResponse("Hello, world!")
    return render(request, "clientphotogallery/dashboard.html")

def charts(request):
    return render(request, "clientphotogallery/charts.html")

def tables(request):
    return render(request, "clientphotogallery/tables.html")

class UserIsOwner(UserPassesTestMixin):
    def get_gallery(self):
        return get_object_or_404(Gallery,pk=self.kwargs.get('pk'))

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user == self.get_gallery().owner
        else:
            raise PermissionDenied('You must be owner of gallery to edit')

class UserLoginView(LoginView):
    template_name= 'clientphotogallery/login.html'
    next_page = 'list'

class UserRegisterView(CreateView):
    template_name = 'clientphotogallery/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('list')
            
    def form_valid(self, form):
        to_return = super().form_valid(form)

        user = authenticate(
            username = form.cleaned_data["username"],
            password = form.cleaned_data["password1"]
        )
        login(self.request, user)
        return to_return

class GalleryListVew(LoginRequiredMixin,ListView):
    login_url = '/dashboard/login/'
    template_name='clientphotogallery/dashboard.html'
    context_object_name='galleries'

    def get_queryset(self):
        queryset = Gallery.objects.filter(owner=self.request.user).annotate(count_selected=Count('assets__selections'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selections'] = Selection.objects.filter(asset__gallery__owner=self.request.user).values('client__identifier', 'asset__file', 'asset__gallery__title', 'print_count', 'updated','comment')
        return context

class GalleryDetailedView(LoginRequiredMixin, UserIsOwner, DetailView):
    login_url = '/dashboard/login/'
    model=Gallery
    template_name='clientphotogallery/gallerydetail.html'
    context_object_name='gallery'

    def get_queryset(self):
        queryset = Gallery.objects.filter(owner=self.request.user).annotate(count_selected=Count('assets__selections'))
        return queryset

class GalleryCreateView(LoginRequiredMixin, CreateView):
    login_url = '/dashboard/login/'
    form_class = GalleryCreateForm
    model=Gallery
    #fields=['title','description','password']
    template_name='clientphotogallery/gallerycreate.html'
    
    def get_success_url(self):
        return self.request.GET.get('next', reverse_lazy('list'))

    # def get_form(self, form_class=None):
    #     form = super().get_form(form_class)
    #     form.fields['file_field'].widget = forms.ClearableFileInput(attrs={'multiple': True})
    #     return form

    def form_valid(self,form):        
        gallery = form.save(commit=False)
        gallery.owner = self.request.user
        gallery.save()

        with transaction.atomic():
            files = self.request.FILES.getlist('file_field')
            for file in files:
                Asset.objects.create(gallery=gallery, file=file)
        return super().form_valid(form)

class GalleryEditView(LoginRequiredMixin, UserIsOwner, UpdateView):
    template_name = 'clientphotogallery/galleryedit.html'
    form_class = GalleryEditForm
    model = Gallery
    #success_url=reverse_lazy('list')

    def get_success_url(self):
        return self.request.GET.get('next', reverse_lazy('list'))

    def form_valid(self,form):        
        gallery = form.save()
        # gallery.owner = self.request.user
        # gallery.save()

        with transaction.atomic():
            files = self.request.FILES.getlist('file_field')
            for file in files:
                if Asset.objects.filter(file=upload_to_gallery(gallery, file)):
                    raise ValidationError('There is already a file with that name on our system')
                else:
                    Asset.objects.create(gallery=gallery, file=file)
        return super().form_valid(form)

class GalleryDeleteView(LoginRequiredMixin, UserIsOwner, DeleteView):
    login_url = '/dashboard/login/'
    template_name = 'clientphotogallery/gallerydelete.html'
    model = Gallery
    success_url=reverse_lazy('list')
  
class GalleryAssetRemoveView(LoginRequiredMixin, UserIsOwner, DeleteView):
    model = Asset
    
    def get_object(self, queryset=None):
        assetid = self.kwargs['id']
        try:
            asset = self.model.objects.get(id=assetid)
        except asset.DoesNotExist:
            return JsonResponse({"error": "Asset not found."}, status=404)
        return asset
    
    def form_valid(self, request, *args, **kwargs):
        asset = self.get_object()
        asset.delete()
        return JsonResponse({"message": "all ok."}, status=201)

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
    
def ClientLandingView(request):
    
    if request.method == "POST":
        gallery_id  = request.POST.get('gallery_id',request.GET.get('gallery_id'))
        
        if not is_valid_uuid(gallery_id):
            return render(request, "clientphotogallery/clientlanding.html", { "message":"Gallery removed or not found" })
        
        try:
            gallery = Gallery.objects.get(pk=gallery_id)
            return redirect('clientgalleryview', pk=gallery.id)
        except Gallery.DoesNotExist:
            return render(request, "clientphotogallery/clientlanding.html", { "message":"Gallery removed or not found" })
            
    else:
        return render(request, "clientphotogallery/clientlanding.html")

def ClientGalleryView(request, pk=None):
    
    if (not request.session.get('clientData', False)):
        clientData = {}
    else:
        clientData = request.session.get('clientData', False)
    
    gal_session = request.session.get('gallery_password', False)
    gal_pw = request.POST.get('gallery_password',request.GET.get('gallery_password'))
    # clientData = {
    #     'clientid':clientid,
    #     'clientemail':None,
    #     'gallery_password':None,
    #     'selection':[{
    #        'assetid':assetid,
    #        'print_count': printcount,
    #        'comment':comment
    #      }]
    #      'selection':{[2,1,'some comment'],[4,1,'']}
    # }

    if request.method == "GET" or request.method == "POST":
        try:
            gallery = Gallery.objects.get(pk=pk)
        except Gallery.DoesNotExist:
            return render(request, "clientphotogallery/clientlanding.html", { "message":"Gallery removed or not found" })
        
        if gallery.archived or not gallery.enabled:
            return render(request, "clientphotogallery/clientlanding.html", { "message":"Gallery removed or not found" })
        
        if not gallery.password:
            request.session['gallery_password']=gallery.password
            return render(request, "clientphotogallery/clientgalleryview.html", { "gallery":gallery, "clientData":clientData })
        else:
            
            # if password not provided via POST/GET
            if not gal_pw:
                # and no session
                if not gal_session:
                    # ask to submit password
                    return render(request,"clientphotogallery/clientgalleryauth.html", {
                            "gallery_id":gallery.id, 
                            "gallery_title":gallery.title
                            })
                # but session exist
                else:
                    # if password is correct? need here to refactor to consider different galeries user might have accessed
                    if gal_session == gallery.password:
                        print("entered here")
                        #sessionData = '{"clientid":"test"}'
                        return render(request, "clientphotogallery/clientgalleryview.html", { "gallery":gallery, "clientData":clientData }) 
                    # if password is not matching, ask to submit password
                    else:
                        # we need to clear any previous clientData session we migh have
                        try:
                            del request.session['clientData']
                        except KeyError:
                            pass
                        return render(request,"clientphotogallery/clientgalleryauth.html", {
                            "gallery_id":gallery.id, 
                            "gallery_title":gallery.title
                            })
            # password provided via POST/GET
            else:
                # if password is correct, create/update session
                if gal_pw == gallery.password:
                    request.session['gallery_password'] = gal_pw
                    
                    return render(request, "clientphotogallery/clientgalleryview.html", { "gallery":gallery, "clientData":clientData })    
                # if password is not correct, ask to submit password
                else:
                    try:
                        del request.session['clientData']
                    except KeyError:
                        pass
                    return render(request,"clientphotogallery/clientgalleryauth.html", {
                            "gallery_id":gallery.id, 
                            "gallery_title":gallery.title
                            })

        #return ("Hello from client gallery")
    
def clientLogout(request):
    del request.session['clientData']
    del request.session['gallery_password']
    return JsonResponse({"success": "Client logout successfull"})

def clientLogin(request, clientid):
    
    if not request.session.get('gallery_password', False):
        return render(request, "clientphotogallery/clientlanding.html", {"message":"You must have valid session"})

    try:
        client = Client.objects.get(identifier=clientid)
        selections = Selection.objects.filter(client=client)
        clientData = {
            'clientid':client.identifier,
            'selection':list(selections.values('asset_id', 'print_count', 'comment'))
        }
        # request.session['clientData'] = clientData
        # return JsonResponse({"success": "Client login successfull", "clientData": clientData}) 

    except Client.DoesNotExist:
        client = Client(identifier=clientid)
        client.save()
        clientData = {
        'clientid':client.identifier,
        'selection':[]
        }
    
    request.session['clientData'] = clientData
    return JsonResponse({"success": "Client login successfull", "clientData": clientData})

def toggleAssetSelection(request, assetid):
    if not request.session.get('gallery_password', False):
        return render(request, "clientphotogallery/clientlanding.html", {"message":"You must have valid session"})
    
    if not request.session.get('clientData', False):
        return render(request, "clientphotogallery/clientlanding.html", {"message":"You must have valid clientid"})

    clientData = request.session.get('clientData', False)

    try:
        selection = Selection.objects.get(client__identifier=clientData['clientid'], asset__pk=assetid)
        selection.delete()
        
    except Selection.DoesNotExist:
        client = Client.objects.get(identifier=clientData['clientid'])
        asset = Asset.objects.get(pk=assetid)
        selection = Selection(client=client, asset=asset)
        selection.save()

    selections = Selection.objects.filter(client__identifier=clientData['clientid'])
    clientData['selection'] =  list(selections.values('asset_id', 'print_count', 'comment'))

    request.session['clientData'] = clientData

    return JsonResponse({"success": "Selection set", "clientData": clientData})

def setPrintCount(request, assetid, print_count):
    if not request.session.get('gallery_password', False):
        return render(request, "clientphotogallery/clientlanding.html", {"message":"You must have valid session"})

    if not request.session.get('clientData', False):
        return render(request, "clientphotogallery/clientlanding.html", {"message":"You must have valid clientid"})

    clientData = request.session.get('clientData', False)

    try:
        selection = Selection.objects.get(client__identifier=clientData['clientid'], asset__pk=assetid)
        selection.print_count = print_count
        selection.save()
        selections = Selection.objects.filter(client__identifier=clientData['clientid'])
        clientData['selection'] =  list(selections.values('asset_id', 'print_count', 'comment'))

        request.session['clientData'] = clientData
        
        return JsonResponse({"success": "Print count set", "clientData": clientData})
    
    except Selection.DoesNotExist:
        return JsonResponse({"error": "Selection not found"}, status=404)