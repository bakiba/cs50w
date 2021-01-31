from django.shortcuts import render

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
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


