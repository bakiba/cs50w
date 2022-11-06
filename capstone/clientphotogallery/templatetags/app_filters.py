import os
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