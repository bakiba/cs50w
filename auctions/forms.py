from django import forms
from .models import Listing

class ListingForm(forms.ModelForm):
       class Meta:
        model = Listing
        fields = ['title','description','start_bid','category','image_url']
        widgets = {
            'title' : forms.TextInput(attrs={'class': 'form-control'}),
            'description' : forms.Textarea(attrs={'class': 'form-control'}),
            'start_bid' : forms.NumberInput(attrs={'class': 'form-control'}),
            'category' : forms.TextInput(attrs={'class': 'form-control'}),
            'image_url' : forms.TextInput(attrs={'class': 'form-control'}),
        }
    