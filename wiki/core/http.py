from __future__ import unicode_literals
from __future__ import absolute_import
import os
import mimetypes
from datetime import datetime
import urllib

from django.http import HttpResponse
from django.utils.http import http_date
from django.utils import dateformat
from django.utils.encoding import filepath_to_uri
from django.conf import settings as django_settings

from wiki.conf import settings


def django_sendfile_response(request, filepath):
    from sendfile import sendfile
    return sendfile(request, filepath)


def send_file(request, filepath, last_modified=None, filename=None):
    if 'amazonaws' in django_settings.STATIC_URL:
        fullpath = filepath

        if filename:
            mimetype, encoding = mimetypes.guess_type(filename)
        else:
            mimetype, encoding = mimetypes.guess_type(fullpath)

        mimetype = mimetype or 'application/octet-stream'

        file_name = fullpath.split('/')[-1]
        file_url = urllib.urlopen(fullpath)
        f = open(file_name, 'wb')

        if settings.USE_SENDFILE:
            response = django_sendfile_response(request, filepath)
        else:
            response = HttpResponse(file_url.read(), content_type=mimetype)

        if isinstance(last_modified, datetime):
            last_modified = float(dateformat.format(last_modified, 'U'))
        response["Last-Modified"] = http_date(epoch_seconds=last_modified)

        response["Content-Length"] = file_url.info().getheaders("Content-Length")[0]

        if encoding:
            response["Content-Encoding"] = encoding

        if filename:
            filename_escaped = filepath_to_uri(filename)
            response["Content-Disposition"] = "attachment; filename=%s" % filename_escaped
        return response
    else:
        fullpath = filepath
        # Respect the If-Modified-Since header.
        statobj = os.stat(fullpath)
        if filename:
            mimetype, encoding = mimetypes.guess_type(filename)
        else:
            mimetype, encoding = mimetypes.guess_type(fullpath)

        mimetype = mimetype or 'application/octet-stream'

        if settings.USE_SENDFILE:
            response = django_sendfile_response(request, filepath)
        else:
            response = HttpResponse(open(fullpath, 'rb').read(), content_type=mimetype)

        if not last_modified:
            response["Last-Modified"] = http_date(statobj.st_mtime)
        else:
            if isinstance(last_modified, datetime):
                last_modified = float(dateformat.format(last_modified, 'U'))
            response["Last-Modified"] = http_date(epoch_seconds=last_modified)

        response["Content-Length"] = statobj.st_size

        if encoding:
            response["Content-Encoding"] = encoding

        if filename:
            filename_escaped = filepath_to_uri(filename)
            response["Content-Disposition"] = "attachment; filename=%s" % filename_escaped

        return response