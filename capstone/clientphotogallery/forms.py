from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Gallery, User

class GalleryCreateForm(forms.ModelForm):
    file_field = forms.FileField(label='Upload files', required=False, widget=forms.ClearableFileInput(attrs={'multiple': True})) 
    class Meta:
        model = Gallery
        fields = ['title','description','password','enabled']

class GalleryEditForm(forms.ModelForm):
    file_field = forms.FileField(label='Upload files', required=False, widget=forms.ClearableFileInput(attrs={'multiple': True})) 
    class Meta:
        model = Gallery
        fields = ['title','description','password','enabled', 'archived']        

class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User  
        