import re
import markdown2

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """

    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    # Fix for extra new lines added: https://stackoverflow.com/questions/62903909/django-contentfile-unexpected-empty-line-django-core-files-base
    default_storage.save(filename, ContentFile(content.encode('ascii')))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None

def to_html(content):
    """
    Simple implementation of Markdown to HTML using regex
    Struggled with regex for paragraph, tried every stackowerflow regex... eventually gave off and used markdown2
    https://stackoverflow.com/questions/51468095/tokenizing-consecutive-lines-as-paragraphs-in-markdown-with-regular-expressions
    """
    patterns = [
        #('(?:\n{2,}|^)((?:(?![#>*\d.-]).+(?:\n|$))+)','<p>\n\\1</p>\n')
        #('^[A-Za-z].*(?:\n[A-Za-z].*)*','<p>\\1</p>\n')
        #('^(?![#>\-*\d ])((?![#>\-*\d ]).+\n?)+','<p>\n\\1</p>\n')
        #('^#\s(.*)$','<h1>\\1</h1>\n'),
        #('^##\s(.*)$','<h2>\\1</h2>\n')
        ('(?P<para_all>(?:\n{2,}|^)(?P<para_prefix>[ ]{0,3})(?P<para_content>(?:(?![>*+-=\#]|\d+\.|\`{3,})).+(?!\n(?:[=-]+|\`{3,}))(?:\n|$))+)','<p>\\1</p>\n')
    ]
    html_content = content
    for pattern, replacement in patterns:
        html_content = re.sub(pattern, replacement, html_content, flags=re.MULTILINE)
    
    #print(content)
    #print('=====================')
    #print(html_content)
    #print(markdown2.markdown(content))
    #print('=====================')
    #html_content += line
    #return html_content
    return markdown2.markdown(content)
    