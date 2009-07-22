# -*- coding: utf-8 -*-
##
## This file is part of CDS Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008 CERN.
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

"""Unit tests for the urlutils library."""

__revision__ = "$Id$"

import unittest

from cgi import parse_qs
from invenio.config import CFG_SITE_URL
from invenio.testutils import make_test_suite, run_test_suite
from invenio.urlutils import \
     create_AWS_request_url, \
     string_to_numeric_char_reference, \
     make_canonical_urlargd, \
     create_html_link, \
     create_html_mailto, \
     same_urls_p, \
     HASHLIB_IMPORTED, \
     wash_url_argument, \
     create_url

class TestWashUrlArgument(unittest.TestCase):
    def test_wash_url_argument(self):
        """urlutils - washing of URL arguments"""
        self.assertEqual(1,
                         wash_url_argument(['1'], 'int'))
        self.assertEqual("1",
                         wash_url_argument(['1'], 'str'))
        self.assertEqual(['1'],
                         wash_url_argument(['1'], 'list'))
        self.assertEqual(0,
                         wash_url_argument('ellis', 'int'))
        self.assertEqual("ellis",
                         wash_url_argument('ellis', 'str'))
        self.assertEqual(["ellis"],
                         wash_url_argument('ellis', 'list'))
        self.assertEqual(0,
                         wash_url_argument(['ellis'], 'int'))
        self.assertEqual("ellis",
                         wash_url_argument(['ellis'], 'str'))
        self.assertEqual(["ellis"],
                         wash_url_argument(['ellis'], 'list'))

class TestUrls(unittest.TestCase):
    """Tests on URLs"""

    def test_url_creation(self):
        """urlutils - test url creation"""
        self.assertEqual(create_url('http://www.a.com/search',
                                    {'recid':3, 'of':'hb&'},
                                    escape_urlargd=True),
                         'http://www.a.com/search?of=hb%26&amp;recid=3')

        self.assertEqual(create_url('http://www.a.com/search',
                                    {'recid':3, 'of':'hb&'},
                                    escape_urlargd=False),
                         'http://www.a.com/search?of=hb&&amp;recid=3')

    def test_canonical_urlargd_creation(self):
        """urlutils - test creation of canonical URLs"""
        self.assertEqual(make_canonical_urlargd({'a' : 1,
                                                 'b' : '2',
                                                 'b&': '2=',
                                                 ':' : '?&'},
                                                {'a': ('int', 1),
                                                 'b': ('str', 2)}),
                         "?b%26=2%3D&amp;%3A=%3F%26&amp;b=2")

    def test_signed_aws_request_creation(self):
        """urlutils - test creation of signed AWS requests"""

        if not HASHLIB_IMPORTED:
            self.fail("SKIPPED: Hashlib not available, test skipped.")

        signed_aws_request_url = create_AWS_request_url("http://webservices.amazon.com/onca/xml",
                                                        {'AWSAccessKeyId': '00000000000000000000',
                                                         'Service': 'AWSECommerceService',
                                                         'Operation': 'ItemLookup',
                                                         'ItemId': '0679722769',
                                                         'ResponseGroup': 'ItemAttributes,Offers,Images,Reviews',
                                                         'Version': '2009-01-06'},
                                                        "1234567890",
                                                        _timestamp="2009-01-01T12:00:00Z")

        # Are we at least acccessing correct base url?
        self.assert_(signed_aws_request_url.startswith("http://webservices.amazon.com/onca/xml"))

        # Check that parameters with special characters (, :) get correctly
        # encoded/decoded
        ## Note: using parse_qs() url-decodes the string
        self.assertEqual(parse_qs(signed_aws_request_url)["ResponseGroup"],
                         ['ItemAttributes,Offers,Images,Reviews'])
        self.assert_('ItemAttributes%2COffers%2CImages%2CReviews' \
                     in signed_aws_request_url)

        self.assertEqual(parse_qs(signed_aws_request_url)["Timestamp"],
                         ['2009-01-01T12:00:00Z'])

        # Check signature exists and is correct
        self.assertEqual(parse_qs(signed_aws_request_url)["Signature"],
                         ['Nace+U3Az4OhN7tISqgs1vdLBHBEijWcBeCqL5xN9xg='])
        self.assert_('Nace%2BU3Az4OhN7tISqgs1vdLBHBEijWcBeCqL5xN9xg%3D&Operation' \
                     in signed_aws_request_url)

        # Continute with an additional request
        signed_aws_request_url_2 = \
                                 create_AWS_request_url("http://ecs.amazonaws.co.uk/onca/xml",
                                                        {'AWSAccessKeyId': '00000000000000000000',
                                                         'Actor': 'Johnny Depp',
                                                         'AssociateTag': 'mytag-20',
                                                         'Operation': 'ItemSearch',
                                                         'ResponseGroup': 'ItemAttributes,Offers,Images,Reviews,Variations',
                                                         'SearchIndex': 'DVD',
                                                         'Service': 'AWSECommerceService',
                                                         'Sort': 'salesrank',
                                                         'Version': '2009-01-01'},
                                                        "1234567890",
                                                        _timestamp="2009-01-01T12:00:00Z")
        # Check signature exists and is correct
        self.assertEqual(parse_qs(signed_aws_request_url_2)["Signature"],
                         ['TuM6E5L9u/uNqOX09ET03BXVmHLVFfJIna5cxXuHxiU='])

    def test_same_urls_p(self):
        """urlutils - test checking URLs equality"""
        self.assertEqual(same_urls_p(CFG_SITE_URL + '?a=b&c=d&e=f',
                                     CFG_SITE_URL + '?e=f&c=d&a=b'),
                         True)

        self.assertEqual(same_urls_p(CFG_SITE_URL + '?a=b&c=d&e=f&ln=fr',
                                     CFG_SITE_URL + '?e=f&c=d&a=b&ln=en'),
                         False)

class TestHtmlLinks(unittest.TestCase):
    """Tests on HTML links"""

    def test_html_link_creation(self):
        """urlutils - test creation of HTML links"""
        # Check with various encoding and escaping traps
        self.assertEqual(create_html_link('http://www.a.com',
                                          {'a' : 1,
                                           'b' : '2',
                                           'b&': '2=',
                                           ':' : '?'},
                                          'my label > & better than yours',
                                          {'style': 'color:#f00',
                                           'target': "_blank"}),
                         '<a href="http://www.a.com?a=1&amp;%3A=%3F&amp;b%26=2%3D&amp;b=2" style="color:#f00" target="_blank">my label > & better than yours</a>')

    def test_html_link_creation_no_argument_escaping(self):
        """urlutils - test creation of HTML links, without arguments escaping"""
        self.assertEqual(create_html_link('http://www.a.com',
                                          {'a' : 1,
                                           'b' : '2',
                                           'b&': '2=',
                                           ':' : '?'},
                                          'my label > & better than yours',
                                          {'style': 'color:#f00',
                                           'target': "_blank"},
                                          escape_urlargd=False),
                         '<a href="http://www.a.com?a=1&amp;:=?&amp;b&=2=&amp;b=2" style="color:#f00" target="_blank">my label > & better than yours</a>')

    def test_html_link_creation_no_attribute_escaping(self):
        """urlutils - test creation of HTML links, without attributes escaping"""
        self.assertEqual(create_html_link('http://www.a.com',
                                          {'a' : 1,
                                           'b' : '2',
                                           'b&': '2=',
                                           ':' : '?'},
                                          'my label > & better than yours',
                                          {'style': 'color:#f00',
                                           'target': "_blank"},
                                          escape_linkattrd=False),
                         '<a href="http://www.a.com?a=1&amp;%3A=%3F&amp;b%26=2%3D&amp;b=2" style="color:#f00" target="_blank">my label > & better than yours</a>')

    def test_string_to_numeric_char_reference(self):
        """urlutils - test numeric character conversion from string"""

        self.assertEqual(string_to_numeric_char_reference('abc123'),
                         "&#97;&#98;&#99;&#49;&#50;&#51;")

        self.assertEqual(string_to_numeric_char_reference('\/&;,#$%~é'),
                         "&#92;&#47;&#38;&#59;&#44;&#35;&#36;&#37;&#126;&#195;&#169;")

class TestEmailObfuscationMode(unittest.TestCase):
    """Tests on HTML mailto links creation and obfuscation modes"""

    def test_html_mailto_obfuscation_mode_minus1(self):
        """urlutils - test creation of HTML "mailto" links, obfuscation mode -1"""
        self.assertEqual(create_html_mailto('juliet@cds.cern.ch',
                                            subject='Hey there',
                                            body='Lunch at 8pm?\ncu!',
                                            bcc='romeo@cds.cern.ch',
                                            link_label="Date creator",
                                            linkattrd={'style': 'text-decoration: blink'},
                                            email_obfuscation_mode=-1),
                         '')

    def test_html_mailto_obfuscation_mode_0(self):
        """urlutils - test creation of HTML "mailto" links, obfuscation mode 0"""
        self.assertEqual(create_html_mailto('juliet@cds.cern.ch',
                                            subject='Hey there',
                                            body='Lunch at 8pm?\ncu!',
                                            bcc='romeo@cds.cern.ch',
                                            link_label="Date creator",
                                            linkattrd={'style': 'text-decoration: blink'},
                                            email_obfuscation_mode=0),
                         '<a href="mailto:juliet@cds.cern.ch?body=Lunch%20at%208pm%3F%0D%0Acu%21&amp;bcc=romeo%40cds.cern.ch&amp;subject=Hey%20there" style="text-decoration: blink">Date creator</a>')

    def test_html_mailto_obfuscation_mode_1(self):
        """urlutils - test creation of HTML "mailto" links, obfuscation mode 1"""
        self.assertEqual(create_html_mailto('juliet@cds.cern.ch',
                                            subject='Hey there',
                                            body='Lunch at 8pm?\ncu!',
                                            bcc='romeo@cds.cern.ch',
                                            link_label="Date creator",
                                            linkattrd={'style': 'text-decoration: blink'},
                                            email_obfuscation_mode=1),
                         '<a href="mailto:juliet [at] cds [dot] cern [dot] ch?body=Lunch%20at%208pm%3F%0D%0Acu%21&amp;bcc=romeo%40cds.cern.ch&amp;subject=Hey%20there" style="text-decoration: blink">Date creator</a>')

    def test_html_mailto_obfuscation_mode_2(self):
        """urlutils - test creation of HTML "mailto" links, obfuscation mode 2"""
        self.assertEqual(create_html_mailto('juliet@cds.cern.ch',
                                            subject='Hey there',
                                            body='Lunch at 8pm?\ncu!',
                                            bcc='romeo@cds.cern.ch',
                                            link_label="Date creator",
                                            linkattrd={'style': 'text-decoration: blink'},
                                            email_obfuscation_mode=2),
                         '<a href="mailto:&#106;&#117;&#108;&#105;&#101;&#116;&#64;&#99;&#100;&#115;&#46;&#99;&#101;&#114;&#110;&#46;&#99;&#104;?body=Lunch%20at%208pm%3F%0D%0Acu%21&amp;bcc=romeo%40cds.cern.ch&amp;subject=Hey%20there" style="text-decoration: blink">Date creator</a>')

    def test_html_mailto_obfuscation_mode_3(self):
        """urlutils - test creation of HTML "mailto" links, obfuscation mode 3"""
        self.assertEqual(create_html_mailto('juliet@cds.cern.ch',
                                            subject='Hey there',
                                            body='Lunch at 8pm?\ncu!',
                                            bcc='romeo@cds.cern.ch',
                                            link_label="Date creator",
                                            linkattrd={'style': 'text-decoration: blink'},
                                            email_obfuscation_mode=3),
                         '<script language="JavaScript" type="text/javascript">document.write(\'>a/<rotaerc etaD>"knilb :noitaroced-txet"=elyts "ereht02%yeH=tcejbus;pma&hc.nrec.sdc04%oemor=ccb;pma&12%ucA0%D0%F3%mp802%ta02%hcnuL=ydob?hc.nrec.sdc@teiluj:otliam"=ferh a<\'.split("").reverse().join(""))</script>')

    def test_html_mailto_obfuscation_mode_4(self):
        """urlutils - test creation of HTML "mailto" links, obfuscation mode 4"""
        self.assertEqual(create_html_mailto('juliet@cds.cern.ch',
                                            subject='Hey there',
                                            body='Lunch at 8pm?\ncu!',
                                            bcc='romeo@cds.cern.ch',
                                            link_label="Date creator",
                                            linkattrd={'style': 'text-decoration: blink'},
                                            email_obfuscation_mode=4),
                         'juliet<img src="%(CFG_SITE_URL)s/img/at.gif" alt=" [at] " style="vertical-align:baseline" />cds<img src="%(CFG_SITE_URL)s/img/dot.gif" alt=" [dot] " style="vertical-align:bottom"  />cern<img src="%(CFG_SITE_URL)s/img/dot.gif" alt=" [dot] " style="vertical-align:bottom"  />ch' % \
                         {'CFG_SITE_URL': CFG_SITE_URL})


TEST_SUITE = make_test_suite(TestWashUrlArgument,
                             TestUrls,
                             TestHtmlLinks,
                             TestEmailObfuscationMode)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
