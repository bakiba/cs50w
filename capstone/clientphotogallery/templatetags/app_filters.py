import os
from collections import OrderedDict
from django import template

register = template.Library()

@register.filter
def asset_in_listdic(list, id):
    if not any(d['asset_id'] == id for d in list):
        return False
    else:
        return True

@register.filter
def get_print_count(list, id):
    for item in list:
        if item['asset_id'] == id:
            return item['print_count']
    return 1

@register.filter
def filename(value):
    return os.path.basename(value)

@register.filter
def filenamenoext(value):
    return os.path.splitext(filename(value))[0]

@register.filter
def clientselectionsassets(data):
    # this filter will take selections dictionay and group it by gallery and clientid and aggregate list of assets
    # thanks to https://stackoverflow.com/a/54249069
    d = OrderedDict()
    for l in data:
        d.setdefault((l['asset__gallery__title'], l['client__identifier']), set()).add(filenamenoext(l['asset__file']))
    
    return [{'asset__gallery__title': k[0], 'client__identifier': k[1], 'asset__file': ", ".join(list(v.pop() if len(v) == 1 else v))} for k, v in d.items()] 

@register.filter
def clientselectionsprints(data):
    d = OrderedDict()
    for l in data:
        d.setdefault((l['asset__gallery__title'], filenamenoext(l['asset__file'])), set()).add(l['print_count'])
    return [{'asset__gallery__title': k[0], 'asset__file': k[1], 'print_count': sum(list(v))} for k, v in d.items()] 