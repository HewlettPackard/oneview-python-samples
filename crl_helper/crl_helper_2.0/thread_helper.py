# -*- coding: utf-8 -*-
###
# (C) Copyright (2012-2018) Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###

import threading
import time
import sys
import ldap3
import urllib.request
import logging
import socket
import requests
import urllib.error
from socket import timeout

stat = 1
stat1 = 1
msg = ''
logging.basicConfig(filename="crl_helper.log", level=logging.DEBUG)
log = logging.getLogger(__name__)


# This function helps in printing dots(......) for showing progress
class myThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while stat == 1:
            print(".", end='')
            sys.stdout.flush()
            time.sleep(0.5)


# This function helps in printing time while uploading CRLs to appliance
class myTimeThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        count = 0
        print('\n', end='\r')
        while stat1 == 1:
            print("\r%s %d secs" % (msg, count), end='')
            time.sleep(1)
            count = count + 1


# This function helps in printing time while downloading CRLs to the local machine
class myTimeThread1(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.count = 0

    def run(self):
        self.count = 0
        print('\n', end='\r')
        while stat1 == 1:
            print("\r%s %.2f secs" % (msg, self.count), end='')
            time.sleep(0.5)
            self.count = self.count + 0.5


# This function downloads CRLs from HTTP URLs with a read timeout
class readwithlimitldap(threading.Thread):

    def __init__(self, ldapserver, queue, successivetimeout):
        threading.Thread.__init__(self)
        self.ldapserver = ldapserver
        self.successivetimeout = successivetimeout
        self.queue = queue

    def run(self):
        try:
            ldap_conn = ldap3.Connection(self.ldapserver, auto_bind=True, receive_timeout=self.successivetimeout)
            self.queue.put(ldap_conn)
        except Exception as e:
            self.queue.put(e)


# This function downloads CRLs from LDAP URLs with a read timeout
class readwithlimithttp(threading.Thread):

    def __init__(self, url, maxreadtime, maxtime, proxyurl, queue):
        threading.Thread.__init__(self)
        self.url = url
        self.maxreadtime = maxreadtime
        self.queuehttp = queue
        self.maxtime = maxtime
        self.proxyurl = proxyurl

    def run(self):
        if self.proxyurl == '':
            proxy_handler = urllib.request.ProxyHandler({})
        else:
            proxies = {"http": self.proxyurl}
            proxy_handler = urllib.request.ProxyHandler(proxies)
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)
        socket.setdefaulttimeout(self.maxtime)
        try:

            x = urllib.request.urlopen(self.url, timeout=self.maxreadtime)
            y = x.read()
            self.queuehttp.put(y)
            return

        except urllib.error.HTTPError as e:
            self.queuehttp.put(e)
            return

        except urllib.error.URLError as e:
            self.queuehttp.put(e)
            return

        except timeout as e:
            self.queuehttp.put(e)
            return

        except Exception as e:
            self.queuehttp.put(e)
            return


# This function downloads CRL metadata from HTTP URLs with a read timeout
class readinfohttp(threading.Thread):

    def __init__(self, url, maxtime, maxcrlsize, proxyurl, queue):
        threading.Thread.__init__(self)
        self.maxtime = maxtime
        self.maxcrlsize = maxcrlsize
        self.url = url
        self.queuehttp = queue
        self.proxyurl = proxyurl

    def run(self):
        if self.proxyurl == '':
            proxy_handler = urllib.request.ProxyHandler({})
        else:
            proxies = {"http": self.proxyurl}
            proxy_handler = urllib.request.ProxyHandler(proxies)
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)
        socket.setdefaulttimeout(self.maxtime)
        try:
            x = urllib.request.urlopen(urllib.request.Request(self.url, method='HEAD'))
            self.queuehttp.put(x)
            return

        except urllib.error.HTTPError as e:
            self.queuehttp.put(e)
            return

        except timeout as e:
            self.queuehttp.put(e)
            return

        except urllib.error.URLError as e:
            self.queuehttp.put(e)
            return

        except TimeoutError as e:
            self.queuehttp.put(e)
            return

        except Exception as e:
            self.queuehttp.put(e)
            return


# This function uploads CRL to appliance with a upload timeout
class uploadcrls(threading.Thread):

    def __init__(self, maxtime, headers, url, uploadtimeout, filename, crlaliaslist, postqueue, proxyurl):
        threading.Thread.__init__(self)
        self.maxtime = maxtime
        self.headers = headers
        self.url = url
        self.uploadtimeout = uploadtimeout
        self.filename = filename
        self.crlaliaslist = crlaliaslist
        self.postqueue = postqueue
        self.proxyurl = proxyurl

    def run(self):
        f = open('crls/' + self.filename, 'rb')
        files = {'file': ('crls/'+self.filename, f, 'application/pkix-crl')}
        socket.setdefaulttimeout(self.maxtime)
        try:
            if self.proxyurl is []:
                response = requests.put(self.url, files=files, headers=self.headers, verify=False,
                                        timeout=self.uploadtimeout)
                self.postqueue.put(response)
                f.close()
            else:
                proxies = {'http': self.proxyurl}
                response = requests.put(self.url, files=files, headers=self.headers, verify=False, proxies=proxies,
                                        timeout=self.uploadtimeout)
                f.close()
                self.postqueue.put(response)
            return
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            self.postqueue.put(e)
            return
        except (requests.exceptions.HTTPError, requests.exceptions.RequestException) as e:
            self.postqueue.put(e)
            return
        except timeout as e:
            self.postqueue.put(e)
            return
        except Exception as e:
            self.postqueue.put(e)
            return
