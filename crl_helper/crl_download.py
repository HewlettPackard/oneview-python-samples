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
import ssl
import json
import ast
import logging
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
maxreadtime=keys['crl.download.read.timeout']
maxlogintries = keys['appliance.login.retries']
maxtimelogin = keys['appliance.rest.read.timeout']
maxresttime = keys['appliance.rest.connection.timeout']

threadlock = threading.Lock()


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

    def run(self):
        threadlock.acquire()
        thread_helper.msg = "Downloading CRL issued by the certificate with aliasname " + self.crlaliasname + "...."
        thread_helper.stat1 = 1
        thread2 = thread_helper.myTimeThread1()
        thread2.daemon = True
        thread2.start()
        for i in self.urllist:
            self.url = i
            index = self.url.rfind("/")
            self.filename = self.url[(index + 1):]
            size = 0
            if os.path.isdir('crls'):
                if os.path.isfile('crls/' + self.filename):
                    log.info("%s, The CRL from the URL %s has already been downloaded" %
                             (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), self.url))
                    file = open('crlfilename.txt', 'a')
                    file.write(self.filename + str(",") + self.url + str(",") + self.crlaliasname + str("\n"))
                    file.close()
                    continue
            if self.proxyurl == '':
                proxy_handler = urllib.request.ProxyHandler({})
            else:
                proxies = {"http": self.proxyurl}
                proxy_handler = urllib.request.ProxyHandler(proxies)
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)
            socket.setdefaulttimeout(int(maxtime))
            flag = 3
            error = ''
            for i in range(int(maxtries)):
                try:
                    x = urllib.request.urlopen(urllib.request.Request(self.url, method='HEAD'))
                    flag = 0
                    break

                except urllib.error.HTTPError as e:
                    error = e
                    flag = 1
                    break

                except timeout as e:
                    error = e
                    flag = 4

                except urllib.error.URLError as e:
                    error = e
                    flag = 1
                    if not isinstance(error.reason, timeout):
                        break

                except TimeoutError as e:
                    error = e
                    flag = 2

                except Exception as e:
                    error = e
                    flag = 5
                    break
            if flag == 1:
                if "unknown url type" in str(error):
                    log.error("%s, %s while fetching CRL Headers from %s. Only http protocol is supported for CRL DP "
                              "location" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), error, self.url))
                    continue
                else:
                    log.error("%s, %s while fetching CRL Headers from %s" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime())
                                                                             , error, self.url))
                    continue
            elif flag == 2:
                log.error("%s, Timeout while fetching CRL Headers from %s.Check for network or proxy issues" %
                          (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), self.url))
                continue
            elif flag == 4:
                log.error("%s, Socket timed out while fetching headers from %s" % (
                    strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), self.url))
                continue
            elif flag == 5:
                log.error("%s, Unexpected error %s occured while downloading CRL headers from %s" % (
                    strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), error, self.url))
                continue
            elif ('Content-Length' in x.info() and flag == 0 and (
                    int(x.info()['Content-Length']) > int(maxcrlsize) * 1000)):
                log.error("%s, size  of crl %s exceeded" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), self.url))
                continue
            else:
                if 'Content-Length' in x.info():
                    size = x.info()['Content-Length']
                count = 0
                timenow, timeend = 0, 0
                socket.setdefaulttimeout(int(maxtime))
                for i in range(int(maxtries)):

                    try:
                        timenow = time.time()
                        x = urllib.request.urlopen(self.url, timeout=int(maxreadtime))
                        timeend = time.time()
                        flag = 0
                        break

                    except urllib.error.HTTPError as e:
                        s = e
                        count = count + 1
                        flag = 1
                        break
                    except urllib.error.URLError as e:
                        s = e
                        count = count + 1
                        flag = 1
                        if not isinstance(s.reason, timeout):
                            break
                        continue

                    except timeout as e:
                        s = e
                        count = count + 1
                        flag = 4
                        continue
                    except Exception as e:
                        s = e
                        flag = 5
                        break
                if flag == 1:
                    log.error("%s, %s - for url %s" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), s, self.url))
                    continue
                elif flag == 2:
                    log.error(
                        "%s, %s - Timeout while downloading CRL from %s,tried to download for %d times.Check for "
                        "network or proxy issues" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), s, self.url, count))
                    continue
                elif flag == 4:
                    log.error(
                        "%s, %s - Socket timed out error while downloading CRL from %s,tried to download for %d times" %
                        (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), s, self.url, count))
                    continue
                elif flag == 5:
                    log.error("%s, Unexpected Error %s occured while downloading CRL from %s" % (
                        strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), s, self.url))
                    continue
                else:
                    y = x.read()
                    try:
                        if not os.path.isdir('crls'):
                            os.makedirs('crls')

                        file2 = open('crls/' + self.filename, "wb")
                        file2.write(y)
                        file2.close()
                        if size == 0:
                            size = os.path.getsize('crls/' + self.filename)
                        file1 = open("crlfilename.txt", "a")
                        file1.write(self.filename + str(",") + self.url + str(",") + self.crlaliasname + str("\n"))
                        file1.close()
                        log.info("%s, Successfully downloaded %s from %s in %s seconds,size=%s Bytes"
                                 % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), self.filename, self.url,
                                    str(round(timeend - timenow, 2)), str(size)))
                        thread_helper.stat1 = 0
                        print("\nSuccessfully downloaded CRL issued by the certificate with aliasname %s"
                              % self.crlaliasname, end='')
                        self.success = 1
                        continue
                    except IOError as e:
                        log.error("%s, Error is %s while storing CRL issued by the certificate with aliasname %s "
                                  % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e, self.crlaliasname))
                        thread_helper.stat1 = 0
                        print("Error %s while storing CRL issued by the certificate with aliasname %s "
                              % (e, self.crlaliasname))
                        self.success = 1
                        continue
                    except Exception as e:
                        log.error("%s, Error is %s while storing CRL issued by the certificate with aliasname %s "
                                  % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e, self.crlaliasname))
                        thread_helper.stat1 = 0
                        print("Error %s while storing CRL issued by the certificate with aliasname %s "
                              % (e, self.crlaliasname))
                        self.success = 1
                        continue

        if self.success == 0:
            thread_helper.stat1 = 0
            print("\nUnable to download CRL from URL %s. See logs for details." % self.url, end='')
        time.sleep(1)
        threadlock.release()


def dwd(applianceip, proxyurl, sessionid):
    s = []
    crlaliasname, crlcommonname, crllist = [], [], []

    print("\nReading CRL DPs from crl_urls.json", end='')
    try:
        file = open("crl_urls.json", 'r')
    except IOError as e:
        log.error("%s, Error is %s" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e))
        return []
    except Exception as e:
        log.error("%s, Error is %s" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e))
        return []

    try:
        certchains = json.load(file)
    except json.JSONDecodeError as e:
        log.error("%s, Error is %s"% (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()),e))
        file.close()
        return []
    except Exception as e:
        log.error("%s, Error is %s" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e))
        file.close()
        return []
    file.close()

    for i in range(len(certchains)):
        try:
            if len(certchains[i]['aliasName'])==0:
                log.info("%s ,aliasname field is empty" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime())))
                continue
            if len(certchains[i]['CRLDps'])==0:
                log.info("%s ,The CRLDp field for the certificate with aliasname %s is empty"%
                         (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), certchains[i]['aliasName']))
            elif len(certchains[i]['CRLDps'])>1:
                log.info("%s ,Multiple CRLDps found. Taking only the first CRLDp %s"
                         % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()),certchains[i]['CRLDps'][0]))
                crlaliasname.append(certchains[i]['aliasName'])
                crllist.append(certchains[i]['CRLDps'][0])
            else:
                crlaliasname.append(certchains[i]['aliasName'])
                crllist.append(certchains[i]['CRLDps'][0])
            threads = []
            k = 0
        except KeyError as e:
            log.error("%s ,Keyerror %s occurred" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e))
            return []
        except IndexError as e:
            log.error("%s ,Keyerror %s occurred" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e))
            return []
        except Exception as e:
            log.error("%s ,%s occurred" %(strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()),e))
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

    if not (os.path.isfile('crlfilename.txt')):
        print("\nNo CRLs downloaded. Check for possible network or proxy or bad URL issues", end='')
        log.error("%s, No CRLs downloaded. Check for possible network or proxy or bad URL issues" % (
            strftime("%Y-%m-%d %H:%M:%S UTC", gmtime())))
        return []
    file = open("crlfilename.txt", "r")
    s = file.readlines()
    file.close()
    os.remove("crlfilename.txt")
    print('\nFetched %s CRLs from their URLs' % (str(len(s))), end='')
    log.info('%s, Fetched %s CRLs from their URLs' % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), str(len(s))))
    if len(s) < len(crlaliasname):
        print('\nCould not fetch %s CRLs from their URLs' % ((len(crlaliasname) - len(s))), end='')
        log.info('%s, Could not fetch %s CRLs from their URLs' %
                 (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), (len(crlaliasname) - len(s))))
    return s


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
            gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            request.add_header('Content-Type', 'application/json')
            request.add_header('X-API-Version', '600')
            request.get_method = lambda: 'POST'
            socket.setdefaulttimeout(int(maxresttime))
            response = urllib.request.urlopen(request, context=gcontext, timeout=int(maxtimelogin))
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
            gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            request.add_header('X-API-Version', '600')
            request.add_header('Auth', sessionid)
            request.get_method = lambda: 'DELETE'
            socket.setdefaulttimeout(int(maxresttime))
            response = urllib.request.urlopen(request, context=gcontext, timeout=int(maxtimelogin))
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
