# -*- coding: utf-8 -*-
## $Id$

## This file is part of CDS Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006 CERN.
##
## CDS Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
""" urlutils: tools for managing URL related problems:
- washing,
- redirection
"""

__lastupdated__ = """$Date$"""
__version__ = "$Id$"

from urllib import urlencode
from urlparse import urlparse
from cgi import parse_qs

from xml.sax.saxutils import quoteattr

try:
    from mod_python import apache
except ImportError:
    pass

from invenio.config import cdslang


def wash_url_argument(var, new_type):
    """
    Wash argument into 'new_type', that can be 'list', 'str', 'int', 'tuple' or 'dict'.
    If needed, the check 'type(var) is not None' should be done before calling this function.
    @param var: variable value
    @param new_type: variable type, 'list', 'str', 'int', 'tuple' or 'dict'
    @return as much as possible, value var as type new_type
            If var is a list, will change first element into new_type.
            If int check unsuccessful, returns 0
    """
    out = []
    if new_type == 'list':  # return lst
        if type(var) is list:
            out = var
        else:
            out = [var]
    elif new_type == 'str':  # return str
        if type(var) is list:
            try:
                out = "%s" % var[0]
            except:
                out = ""
        elif type(var) is str:
            out = var
        else:
            out = "%s" % var
    elif new_type == 'int': # return int
        if type(var) is list:
            try:
                out = int(var[0])
            except:
                out = 0
        elif type(var) is int:
            out = var
        elif type(var) is str:
            try:
                out = int(var)
            except:
                out = 0
        else:
            out = 0
    elif new_type == 'tuple': # return tuple
        if type(var) is tuple:
            out = var
        else:
            out = (var,)
    elif new_type == 'dict': # return dictionary
        if type(var) is dict:
            out = var
        else:
            out = {0:var}
    return out

def redirect_to_url(req, url):
    """
    Redirect current page to url.
    @param req: request as received from apache
    @param url: url to redirect to"""
    req.err_headers_out.add("Location", url)
    raise apache.SERVER_RETURN, apache.HTTP_MOVED_PERMANENTLY

def get_client_ip_address(req):
    """ Returns IP address as string from an apache request. """
    return str(req.get_remote_host(apache.REMOTE_NOLOOKUP))

def get_referer(req, replace_ampersands=1):
    """ Return the referring page of a request.
    Referer (wikipedia): Referer is a common misspelling of the word "referrer";
    so common, in fact, that it made it into the official specification of HTTP.
    When visiting a webpage, the referer or referring page is the URL of the
    previous webpage from which a link was followed.
    @param req: request
    @param replace_ampersands: if 1, replace & by &amp; in url (correct HTML cannot contain & characters alone).
    """
    try:
        referer = req.headers_in['Referer']
        if replace_ampersands==1:
            return referer.replace('&', '&amp;')
        return referer
    except KeyError:
        return ''


def drop_default_urlargd(urlargd, default_urlargd):
    lndefault = {}
    lndefault.update(default_urlargd)
    lndefault['ln'] = (str, cdslang)
    
    canonical = {}
    canonical.update(urlargd)
    
    for k, v in urlargd.items():
        try:
            d = lndefault[k]

            if d[1] == v:
                del canonical[k]
                
        except KeyError:
            pass

    return canonical

def make_canonical_urlargd(urlargd, default_urlargd):
    """ Build up the query part of an URL from the arguments passed in
    the 'urlargd' dictionary.  'default_urlargd' is a secondary dictionary which
    contains tuples of the form (type, default value) for the query
    arguments (this is the same dictionary as the one you can pass to
    webinterface_handler.wash_urlargd).

    When a query element has its default value, it is discarded, so
    that the simplest (canonical) url query is returned.

    The result contains the initial '?' if there are actual query
    items remaining.
    """

    canonical = drop_default_urlargd(urlargd, default_urlargd)

    if canonical:
        return '?' + urlencode(canonical, doseq=True)

    return ''


def a_href(text, **kargs):
    """ Build a properly escaped <a href="...">...</a> fragment.

    - text: content of the tag, already html-escaped
    - all the other keyword arguments are quoteattr-escaped.
    """
    
    if '_class' in kargs:
        kargs['class'] = kargs['_class']
        del kargs['_class']
        
    attrs = ['%s=%s' %(k, quoteattr(kargs[k])) for k in kargs.keys()]

    return '<a %s>%s</a>' % (' '.join(attrs), text)


def same_urls_p(a, b):
    """ Compare two URLs, ignoring reorganizing of query arguments """

    ua = list(urlparse(a))
    ub = list(urlparse(b))
    
    ua[4] = parse_qs(ua[4], True)
    ub[4] = parse_qs(ub[4], True)

    return ua == ub
