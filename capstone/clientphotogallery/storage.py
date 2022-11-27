# https://stackoverflow.com/questions/38509054/django-filefield-name-special-chars-replaced-automatically
# https://stackoverflow.com/questions/38509054/django-filefield-name-special-chars-replaced-automatically
import re
from django.core.exceptions import SuspiciousFileOperation
from django.utils.functional import keep_lazy_text
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible

@keep_lazy_text
def get_valid_filename(name):
    """
    Modified get_valid_filename function as I need file names unchanged. Only strip leading and trailing spaces.
    """
    s = str(name).strip()
    #s = re.sub(r"(?u)[^-'\s\w.]", "", s)
    if s in {"", ".", ".."}:
        raise SuspiciousFileOperation("Could not derive file name from '%s'" % name)
    return s

@deconstructible
class CustomFileSystemStorage(FileSystemStorage):

    def get_valid_name(self, name):
        """
        Return a filename, based on the provided filename, that's suitable for
        use in the target storage system.
        """
        return get_valid_filename(name)