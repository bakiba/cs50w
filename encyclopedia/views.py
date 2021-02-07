from django.shortcuts import render
from django import forms
from django.contrib import messages
from django.utils.text import slugify

from . import util
import re

class NewPageForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'class': "form-control"}))
    content = forms.CharField(label="Content", widget=forms.Textarea(attrs={'class': "form-control"}))

def index(request):
    entries = util.list_entries()
    query = request.GET.get('q', '')
    if query != '':
        query = re.sub('\W+','', query)
        found_entries = [ entry for entry in entries if query.lower() in entry.lower() ] 
        if len(found_entries) == 1 and query.lower() in (entry.lower() for entry in entries):
            page = util.get_entry(query)
            if page is not None:
                return render(request, "encyclopedia/page.html", {
                    "page": page,
                    "name": query
                })
        else:
            return render(request, "encyclopedia/search.html", {
                    "query": query,
                    "entries":  found_entries
            })    
    else:
        return render(request, "encyclopedia/index.html", {
            "entries": entries
        })

def page(request, name):
    page = util.get_entry(name)
    if page is not None:
        return render(request, "encyclopedia/page.html", {
            "page": page,
            "name": name
        })
    else:
        return render(request, "encyclopedia/page.html", {
            "page": "Page not found",
            "name": name
        }) 

def newpage(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            # we will use slugify to create safe to write to disk
            title = slugify(form.cleaned_data["title"])
            content = form.cleaned_data["content"]
            if title != "" and title.lower() not in (entry.lower() for entry in util.list_entries()):
                util.save_entry(title, content)
                messages.success(request, f'Page with title "{title}" successfully added.')
                return render(request, "encyclopedia/page.html", {
                    "page": util.get_entry(title),
                    "name": title
                })
            else:
                # we need to add "danger" tag to message to trigger red alert banner in bootstrap
                DANGER = 50;
                messages.add_message(request, DANGER, f'Page with title "{title}" already exists.', extra_tags='danger')
                return render(request, "encyclopedia/newpage.html", {
                    "form": form,
                })
    else:
        return render(request, "encyclopedia/newpage.html", {
            "form": NewPageForm()
        })



