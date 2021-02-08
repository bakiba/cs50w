from django.shortcuts import render
from django import forms
from django.contrib import messages
from django.utils.text import slugify

from . import util
import re
import random

class NewPageForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'class': "form-control"}))
    content = forms.CharField(label="Content", widget=forms.Textarea(attrs={'class': "form-control"}))

def index(request):
    # Rerieve all entries
    entries = util.list_entries()
    # Did user submited search via GET?
    query = request.GET.get('q', '')
    if query != '':
        # It looks like user wants to search for some page
        # clean-up the query string from all non-word characters
        query = re.sub('\W+','', query)
        # Search for all entries mathing query substring
        found_entries = [ entry for entry in entries if query.lower() in entry.lower() ] 
        # We found only one entry and it is complete match, not just part of entry
        # This is beucase if it is exact match, we should return page to user directly
        if len(found_entries) == 1 and query.lower() in (entry.lower() for entry in entries):
            page = util.get_entry(query)
            if page is not None:
                return render(request, "encyclopedia/page.html", {
                    "page": util.to_html(page),
                    "name": query
                })
        else:
            # Show to search results
            return render(request, "encyclopedia/search.html", {
                    "query": query,
                    "entries":  found_entries
            })    
    else:
        # We're not comming from search, so show list of all entries
        return render(request, "encyclopedia/index.html", {
            "entries": entries
        })

def page(request, name):
    # Get page from the disk
    page = util.get_entry(name)
    if page is not None:
        # Return it to user
        return render(request, "encyclopedia/page.html", {
            # Apply Markdown to HTML conversion
            "page": util.to_html(page),
            "name": name
        })
    else:
        # Return page not found in case we can't locate entry
        return render(request, "encyclopedia/page.html", {
            "page": "Page not found",
            "name": name
        }) 

def newpage(request):
    # We submitted create new page form
    if request.method == "POST":
        # Get form data
        form = NewPageForm(request.POST)
        if form.is_valid():
            # we will use slugify to create safe title to write to disk
            title = slugify(form.cleaned_data["title"])
            content = form.cleaned_data["content"]
            # If entry with same title exists, we will throw error
            # Conver title to lower so we do not treat "CSS", "CSs", etc as separate entries
            if title != "" and title.lower() not in (entry.lower() for entry in util.list_entries()):
                # All checks passed, save entry
                util.save_entry(title, content)
                # Show successfull message
                messages.success(request, f'Page with title "{title}" successfully added.')
                # Return the page to user in HTML format
                return render(request, "encyclopedia/page.html", {
                    "page": util.to_html(util.get_entry(title)),
                    "name": title
                })
            else:
                # we need to add "danger" tag to message to trigger red alert banner in bootstrap
                DANGER = 50;
                messages.add_message(request, DANGER, f'Page with title "{title}" already exists.', extra_tags='danger')
                # Retrun form back to user
                return render(request, "encyclopedia/newpage.html", {
                    "form": form,
                })
    else:
        # We're comming from "Create New Page"
        return render(request, "encyclopedia/newpage.html", {
            "form": NewPageForm()
        })
        
def editpage(request, name):
    # We're submitted the edite page via POST
    if request.method == "POST":
        # Get form data from POST
        form = NewPageForm(request.POST)
        if form.is_valid():
            # Get title and data
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            # We will only allow page data to be changed, so if user change title, it will not match the entry name
            if title == name:
                # Title was not changed, save the entry and return the modified page to user
                util.save_entry(title, content)
                messages.success(request, f'Page with title "{title}" successfully edited.')
                return render(request, "encyclopedia/page.html", {
                    "page": util.to_html(util.get_entry(title)),
                    "name": title
                })
            else:
                # Title of the page was also changed, we do not have way of renaming the entry and it could get messy if we would allow to save as new page
                DANGER = 50;
                messages.add_message(request, DANGER, f'Can\'t change page title', extra_tags='danger')
                # We subbmitted form with edite title and now must generate new form with original title and return it back to user
                ret_form = NewPageForm({
                    "title": name,
                    "content": content
                })
                return render(request, "encyclopedia/editpage.html", {
                    "form": ret_form,
                })
    else:
        # We did not submit POST, this is when you click edit link on page
        # Retrieve page
        page = util.get_entry(name)
        if page is not None:
            # Populate the form
            form = NewPageForm({
                "title": name,
                "content": page
            })
            # Send it back to user
            return render(request, "encyclopedia/editpage.html", {
                "form": form
            })
        else:
            # Some error and we could not find requested page
            return render(request, "encyclopedia/page.html", {
                "page": "Page not found",
                "name": name
            })

def randpage(request):
    # Select random entry from list of entries
    rand_title = random.choice(util.list_entries())
    # Fetch the entry from disk
    page = util.get_entry(rand_title)
    # Render page
    if page is not None:
        return render(request, "encyclopedia/page.html", {
            "page": util.to_html(page),
            "name": rand_title
        })
    else:
        return render(request, "encyclopedia/page.html", {
            "page": "Page not found",
            "name": rand_title
        })    


