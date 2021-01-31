from django.shortcuts import render

from . import util
import re

def index(request):
    entries = util.list_entries()
    query = request.GET.get('q', '')
    if query != '':
        page = util.get_entry(re.sub('\W+','', query))
        if page is not None:
            return render(request, "encyclopedia/page.html", {
                "page": page,
                "name": query
            })
        else:
            found_entries = [ entry for entry in entries if query.lower() in entry.lower() ] 
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


