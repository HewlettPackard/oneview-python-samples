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

import urllib.request
import threading
import urllib.error
import urllib
import socket
import os
import time
import json
import ast
import logging
import ldap3
import ldap3.core
import queue
import thread_helper
from time import strftime, gmtime
from socket import timeout

logging.basicConfig(filename="crl_helper.log", level=logging.DEBUG)
log = logging.getLogger(__name__)
separator = "="
keys = {}
with open('download_crl.properties') as f:
    for line in f:
        if separator in line:
            name, value = line.split(separator, 1)
            keys[name.strip()] = value.strip()

maxtries = keys['crl.download.max.retries']
maxcrlsize = keys['crl.upload.maxSize']
maxtime = keys['crl.download.connection.timeout']
maxreadtime = keys['crl.download.read.timeout']
maxlogintries = keys['appliance.login.retries']
maxtimelogin = keys['appliance.rest.read.timeout']
maxresttime = keys['appliance.rest.connection.timeout']
maxsuccessivetimeout = keys['crl.download.read.succesivetimeout']

threadlock = threading.Lock()
crlDetails = ''
errorcount = 0


# This object is the implementation of threads for downloading CRLs. Each thread downloads one CRL.
class mythread(threading.Thread):

    def __init__(self, urllist, proxyurl, crlaliasname, appliance, sessionid):
        threading.Thread.__init__(self)
        self.url = ''
        self.filename = ''
        self.proxyurl = proxyurl
        self.crlaliasname = crlaliasname
        self.appliance = appliance
        self.sessionid = sessionid
        self.urllist = urllist
        self.count = 0
        self.success = 0
        self.server = ''
        self.dn = ''
        self.attributes = ''
        self.protocoltype = 0
        self.ldapdict = {}
        self.scope = ''

    def run(self):
        global crlDetails, errorcount
        threadlock.acquire()

        for url in self.urllist:
            self.success = 0
            self.url = url
            self.url.strip()
            if len(self.url) > 35:
                self.printurl = self.url[0:32] + ' ...'
            else:
                self.printurl = self.url
            thread_helper.msg = "Downloading CRL from " + self.printurl + " issued by the certificate with aliasname " + \
                                self.crlaliasname + "...."
            thread_helper.stat1 = 1
            thread2 = thread_helper.myTimeThread1()
            thread2.daemon = True
            thread2.start()
            if 'http://' in self.url:
                self.protocoltype = 1
                if '.crl' in self.url and not(self.url.rfind('/') == -1):
                    self.filename = self.url[(self.url.rfind('/') + 1):(self.url.rfind('.crl')+4)]
                else:
                    self.filename = self.crlaliasname + '.crl'
            elif 'ldap://' in self.url:
                self.protocoltype = 2
                self.ldapdict = ldap3.utils.uri.parse_uri(self.url)
                self.filename = self.crlaliasname + '.crl'
                if self.ldapdict is None:
                    log.error("%s, Invalid LDAP URL %s" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), self.url))
                    thread_helper.stat1 = 0
                    print("\nInvalid LDAP URL %s" % self.printurl, end='')
                    continue
            elif 'ftp://' in self.url:
                self.protocoltype = 3
                pass
            else:
                log.error("%s, Invalid file download protocol in url %s" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()),
                                                                            self.url))
                thread_helper.stat1 = 0
                print("\nInvalid file download protocol in url %s" % self.printurl, end='')
                continue

            if os.path.isdir('crls'):
                if os.path.isfile('crls/' + self.filename):
                    log.info("%s, The CRL from the URL %s has already been downloaded" %
                             (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), self.url))
                    self.success = 1
                    crlDetails = crlDetails + self.filename + str("scrysv789") + self.url + str("scrysv789") \
                                 + self.crlaliasname + str("\delimiter12345")
                    break
            if self.protocoltype == 1:
                self.httpdownload()
            elif self.protocoltype == 2:
                self.ldapdownload()
            if self.success == 1:
                thread_helper.stat1 = 0
                time.sleep(1)
                break
            if self.success == 0:
                errorcount = errorcount + 1
                thread_helper.stat1 = 0
                print("\nUnable to download CRL from the URL %s. See logs for details" % self.printurl, end='')
            if self.success == 2:
                errorcount = errorcount + 1
        time.sleep(0.5)
        threadlock.release()

    # This script downloads CRLs from HTTP URLs
    def httpdownload(self):
        global crlDetails
        queuehttp = queue.Queue()
        for i in range(int(maxtries)):
            err = ''
            queuehttp.queue.clear()
            threadinfo = thread_helper.readinfohttp(self.url, int(maxtime), int(maxcrlsize), self.proxyurl, queuehttp)
            threadinfo.daemon = True
            threadinfo.start()
            threadinfo.join(int(maxreadtime))
            if not threadinfo.isAlive():
                headerinfo = queuehttp.get()
                break
            else:
                err = 'Timeout Exception'
            if not err == '':
                log.error("%s, Timeout Exception while fetching CRL meta data from %s" %
                          (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), self.url))
                return
        if not headerinfo.__class__.__name__ == 'HTTPResponse':
            log.error("%s, Error is %s while fetching CRL headers from %s" %
                      (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), str(headerinfo), self.url))
            return

        if 'Content-Length' in headerinfo.info():
            size = headerinfo.info()['Content-Length']

        elif ('Content-Length' in headerinfo.info() and (
                int(headerinfo.info()['Content-Length']) > int(self.maxcrlsize) * 1000)):
            log.error("%s, size  of crl from %s exceeded" %
                      (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), self.url))
            return

        for i in range(int(maxtries)):
            err = ''
            queuehttp.queue.clear()
            threadnew = thread_helper.readwithlimithttp(self.url, int(maxsuccessivetimeout), int(maxtime), self.proxyurl, queuehttp)
            threadnew.daemon = True
            timenow = time.time()
            threadnew.start()
            threadnew.join(int(maxreadtime))
            timeend = time.time()
            if not threadnew.isAlive():
                crldata = queuehttp.get()
                break
            else:
                err = 'Timeout Exception'
        if not err == '':
            log.error("%s, Timeout Exception while downloading the CRL from %s" %
                      (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), self.url))
            return
        if not str(crldata.__class__) == '<class \'bytes\'>':
            log.error("%s, Error is %s while fetching CRL from %s" %
                      (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), str(crldata), self.url))
            return

        try:
            if not os.path.isdir('crls'):
                os.makedirs('crls')
            file2 = open('crls/' + self.filename, "wb")
            file2.write(crldata)
            file2.close()
            if size == 0:
                size = os.path.getsize('crls/' + self.filename)
            crlDetails = crlDetails + self.filename + str("scrysv789") + self.url + str("scrysv789") + \
                         self.crlaliasname + str("\delimiter12345")
            log.info("%s, Successfully downloaded %s from %s in %s seconds,size=%s Bytes"
                     % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), self.filename, self.url,
                        str(round(timeend - timenow, 2)), str(size)))
            thread_helper.stat1 = 0
            print("\nSuccessfully downloaded CRL issued by the certificate with aliasname %s"
                  % self.crlaliasname, end='')
            self.success = 1
            return
        except IOError as e:
            log.error("%s, Error is %s while storing CRL issued by the certificate with aliasname %s "
                      % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e, self.crlaliasname))
            thread_helper.stat1 = 0
            print("\nError %s while storing CRL issued by the certificate with aliasname %s "
                  % (e, self.crlaliasname), end='')
            self.success = 2
            return
        except Exception as e:
            log.error("%s, Error is %s while storing CRL issued by the certificate with aliasname %s "
                      % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e, self.crlaliasname))
            thread_helper.stat1 = 0
            print("\nError %s while storing CRL issued by the certificate with aliasname %s "
                  % (e, self.crlaliasname), end='')
            self.success = 2
            return

    # This function downloads CRLs through LDAP CRLs
    def ldapdownload(self):
        global crlDetails
        self.server = self.ldapdict['host']
        self.attributes = self.ldapdict['attributes']
        if self.ldapdict['base'] is None:
            self.dn = ''
        else:
            self.dn = self.ldapdict['base']
        if self.ldapdict['scope'] is None:
            self.scope = ldap3.BASE
        elif self.ldapdict['scope'] is 'SUBTREE':
            self.scope = ldap3.SUBTREE
        elif self.ldapdict['scope'] is 'LEVEL':
            self.scope = ldap3.LEVEL
        if self.ldapdict['filter'] is None:
            self.filter = '(objectClass=*)'
        else:
            self.filter = '(' + self.ldapdict['filter'] + ')'
        err = ''
        q = queue.Queue()
        for i in range(int(maxtries)):
            timenow = time.time()
            try:
                q.queue.clear()
                ldapserver = ldap3.Server(self.server, connect_timeout=int(maxtime))
                threadnew = thread_helper.readwithlimitldap(ldapserver, q, int(maxsuccessivetimeout))
                threadnew.daemon = True
                threadnew.start()
                threadnew.join(int(maxreadtime))
                if not threadnew.isAlive():
                    ldap_conn = q.get()
                    if not (str(ldap_conn.__class__.__name__) is 'Connection'):
                        log.error("%s, Error is %s while downloading CRL from the URL %s" %
                                  (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), ldap_conn, self.url))
                        return
                else:
                    err = 'Timeout Exception'
                    continue
                ldap_conn.search(search_base=self.dn, search_filter=self.filter, search_scope=self.scope,
                                 attributes=self.attributes)
                timeend = time.time()
                break
            except ldap3.core.exceptions.LDAPException as e:
                err = e
                continue
            except ldap3.core.exceptions.LDAPOperationResult as e:
                err = e
                continue
            except Exception as e:
                err = e
                continue
        if not err == '':
            log.error("%s, Error is %s while downloading CRL from URL %s"
                      % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), err, self.url))
            return
        try:
            entries = ldap_conn.entries[0][self.ldapdict['attributes'][0]].value
            if len(entries) > int(maxcrlsize) * 1000:
                log.error("%s, size  of crl from %s exceeded" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), self.url))
                return
        except (KeyError, IndexError, Exception) as e:
            log.error("%s, Unable to parse the response from the LDAP URL %s. Error is %s" %
                      (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), self.url, e))
            return
        try:
            if not os.path.isdir('crls'):
                os.makedirs('crls')
            file = open('crls/' + self.filename, "wb")
            file.write(entries)
            file.close()
            size = os.path.getsize('crls/' + self.filename)
            crlDetails = crlDetails + self.filename + str("scrysv789") + self.url + str("scrysv789") + \
                         self.crlaliasname + str("\delimiter12345")
            log.info("%s, Successfully downloaded %s from %s in %s seconds,size=%s Bytes"
                     % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), self.filename, self.url,
                        str(round(timeend - timenow, 2)), str(size)))
            thread_helper.stat1 = 0
            print("\nSuccessfully downloaded CRL issued by the certificate with aliasname %s"
                  % self.crlaliasname, end='')
            self.success = 1
            return
        except IOError as e:
            log.error("%s, Error is %s while storing CRL issued by the certificate with aliasname %s "
                      % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e, self.crlaliasname))
            thread_helper.stat1 = 0
            print("\nError %s while storing CRL issued by the certificate with aliasname %s "
                  % (e, self.crlaliasname), end='')
            self.success = 2
            return
        except Exception as e:
            log.error("%s, Error is %s while storing CRL issued by the certificate with aliasname %s "
                      % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e, self.crlaliasname))
            thread_helper.stat1 = 0
            print("\nError %s while storing CRL issued by the certificate with aliasname %s "
                  % (e, self.crlaliasname), end='')
            self.success = 2
            return


# This function reads the crl_urls.json file to get the certificate aliasnames and CRL DPs. Then it downloads CRLs
# and stores them in a temporary folder.
def download(applianceip, proxyurl, sessionid):
    global crlDetails, errorcount
    crlaliasname, crlcommonname, crllist = [], [], []

    print("\nReading CRL DPs from crl_urls.json", end='')
    try:
        file = open("crl_urls.json", 'r')
    except IOError as e:
        log.error("%s, Error is %s" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e))
        thread_helper.stat = 0
        print("\nError while reading crl_urls.json file. See logs for details", end='')
        return []
    except Exception as e:
        log.error("%s, Error is %s" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e))
        thread_helper.stat = 0
        print("\nError while reading crl_urls.json file. See logs for details", end='')
        return []

    try:
        certchains = json.load(file)
    except json.JSONDecodeError as e:
        log.error("%s, Error is %s" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e))
        thread_helper.stat = 0
        print("\nError while reading crl_urls.json file. See logs for details", end='')
        file.close()
        return []
    except Exception as e:
        log.error("%s, Error is %s" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e))
        thread_helper.stat = 0
        print("\nError while reading crl_urls.json file. See logs for details", end='')
        file.close()
        return []
    file.close()

    for i in range(len(certchains)):
        try:
            if len(certchains[i]['aliasName']) == 0:
                log.info("%s ,aliasname field is empty" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime())))
                continue
            if len(certchains[i]['CRLDps']) == 0:
                log.info("%s ,The CRLDp field for the certificate with aliasname %s is empty" %
                         (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), certchains[i]['aliasName']))
            else:
                crlaliasname.append(certchains[i]['aliasName'])
                crllist.append(certchains[i]['CRLDps'])
            threads = []
            k = 0
        except KeyError as e:
            log.error("%s ,Keyerror %s occurred" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e))
            thread_helper.stat = 0
            print("\nError while reading crl_urls.json file. See logs for details", end='')
            return []
        except IndexError as e:
            log.error("%s ,error %s occurred" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e))
            thread_helper.stat = 0
            print("\nError while reading crl_urls.json file. See logs for details", end='')
            return []
        except Exception as e:
            log.error("%s ,%s occurred" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e))
            thread_helper.stat = 0
            print("\nError while reading crl_urls.json file. See logs for details", end='')
            return []
    thread_helper.stat = 0
    print("\nDownloading CRLs from CRL DPs.....", end='')
    for i in range(len(certchains)):
        log.info("%s, Certificate with alias name %s has issued CRLs that can be downloaded from %s"
                 % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), certchains[i]['aliasName'], certchains[i]['CRLDps']))
        mythread.daemon = True
        threads.append(mythread(certchains[i]['CRLDps'], proxyurl, certchains[i]['aliasName'], applianceip, sessionid))
        threads[k].start()
        k = k + 1

    release = False
    while not release:
        count = 0
        for t in threads:
            if t is not None and t.isAlive():
                pass
            else:
                count = count + 1
            if count == len(threads):
                release = True
                break
    thread_helper.stat1 = 0
    thread_helper.stat = 1
    if crlDetails == '':
        print("\nNo CRLs downloaded. Check for possible network or proxy or bad URL issues", end='')
        log.error("%s, No CRLs downloaded. Check for possible network or proxy or bad URL issues" % (
            strftime("%Y-%m-%d %H:%M:%S UTC", gmtime())))
        return []
    crlDetails = crlDetails[:-15]
    s = crlDetails.split('\delimiter12345')
    print('\nFetched %s CRLs from their URLs' % (str(len(s))), end='')
    log.info('%s, Fetched %s CRLs from their URLs' % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), str(len(s))))
    if errorcount > 0:
        print('\nCould not fetch %s CRLs from their URLs' % (errorcount), end='')
        log.info('%s, Could not fetch %s CRLs from their URLs' %
                 (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), (len(crlaliasname) - len(s))))
    return crlDetails


# This function logs into the appliance and returns a session ID if successful
def login(appliance, username, password, proxyurl, flag):
    type = 0
    error = ''
    data = {
        "authLoginDomain": "LOCAL",
        "userName": username,
        "password": password,
        "loginMsgAck": "true"
    }

    url = 'https://' + appliance + '/rest/login-sessions'
    count = 0
    while count < int(maxlogintries):
        try:
            if proxyurl == '':
                proxy_handler = urllib.request.ProxyHandler({})
            else:
                proxies = {"http": proxyurl}
                proxy_handler = urllib.request.ProxyHandler(proxies)
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)
            request = urllib.request.Request(url, data=json.dumps(data).encode('utf8'))
            request.add_header('Content-Type', 'application/json')
            request.add_header('X-API-Version', '600')
            request.get_method = lambda: 'POST'
            socket.setdefaulttimeout(int(maxresttime))
            response = urllib.request.urlopen(request, timeout=int(maxtimelogin))
            sessionID1 = response.read().decode('utf8')
            sessionid = ast.literal_eval(sessionID1)
            auth = sessionid['sessionID']
            return auth
        except urllib.error.HTTPError as e:
            count = count + 1
            type = 1
            error = e
            break

        except urllib.error.URLError as e:
            count = count + 1
            type = 2
            error = e
            if not isinstance(error.reason, socket.timeout):
                break
            else:
                continue

        except timeout as e:
            type = 3
            count = count + 1
            continue

        except Exception as e:
            print('\nUnable to login to appliance %s' % appliance, end='')
            log.error("%s, %s while logging into appliance %s." % (
                strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e, appliance))
            return 1

    if type == 1:
        print('\nUsername or password invalid. Unable to login to appliance %s' % appliance, end='')
        log.error(
            "%s, %s while logging into appliance %s. Check if login credentials are correct" % (
                strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), error, appliance))
        return 1

    if type == 2:
        print('\nInvalid appliance address or proxy. Unable to connect to appliance %s' % appliance, end='')
        log.error("%s, %s while logging into appliance %s. Check if appliance address or proxy is correct" % (
            strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), error, appliance))
        return 1

    if type == 3:
        return ''


# This function logs out of the appliance
def logout(appliance, sessionid, proxyurl):
    count = 0
    error = ''
    url = 'https://' + appliance + '/rest/login-sessions'
    while count < int(maxlogintries):
        try:
            if proxyurl == '':
                proxy_handler = urllib.request.ProxyHandler({})
            else:
                proxies = {"http": proxyurl}
                proxy_handler = urllib.request.ProxyHandler(proxies)
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)
            request = urllib.request.Request(url)
            request.add_header('X-API-Version', '600')
            request.add_header('Auth', sessionid)
            request.get_method = lambda: 'DELETE'
            socket.setdefaulttimeout(int(maxresttime))
            response = urllib.request.urlopen(request, timeout=int(maxtimelogin))
            print('\nLogged out of appliance %s' % appliance, end='')
            log.info('Logged out of appliance %s' % appliance)
            return
        except timeout as e:
            error = e
            count = count + 1
            continue

        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            print('\nUnable to logout of the appliance %s' % appliance, end='')
            log.error('%s ,Unable to logout of appliance %s due to %s' % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()),
                                                                          appliance, e))
            return
        except Exception as e:
            print('\nUnable to logout of the appliance %s' % appliance, end='')
            log.error('%s ,Unable to logout of appliance %s due to %s' % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()),
                                                                          appliance, e))
            return

    print('\nUnable to logout of the appliance %s' % appliance, end='')
    log.error('%s ,Unable to logout of appliance %s due to %s' % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()),
                                                                  appliance, error))
    return
