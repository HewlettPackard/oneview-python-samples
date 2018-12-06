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

import logging
import requests
import ssl
import urllib.request
import json
import shutil
import time
import thread_helper
import os
import crl_download
import socket
from time import strftime, gmtime
from socket import timeout

logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("urllib.request").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
log = logging.basicConfig(filename="crl_helper.log", level=logging.ERROR)
log = logging.getLogger(__name__)
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()
separator = "="
keys = {}
with open('download_crl.properties') as f:
    for line in f:
        if separator in line:
            name, value = line.split(separator, 1)
            keys[name.strip()] = value.strip()
maxlogintries = keys['appliance.login.retries']
maxuploadtries = keys['appliance.upload.retries']
uploadtimeout = keys['crl.upload.write.timeout']
polltries = keys['crl.poll.retries']
polltime = keys['crl.poll.time']
maxtime = keys['appliance.rest.connection.timeout']
maxrestreadtime=keys['appliance.rest.read.timeout']

class validateCrl:

    def __init__(self):
        pass

    def validateAndUpload(self, filenamesandcrls, appliance, proxyurl, sessionid):
        self.filenames = []
        self.url = []
        self.crlaliaslist = []
        self.filenamesandcrls = filenamesandcrls
        self.proxyurl = proxyurl
        i = 0
        self.sessionid = sessionid

        thread_helper.stat = 0
        time.sleep(2)
        print("\nUploading CRLs.....", end='')

        for j in self.filenamesandcrls:
            temp1, temp2, temp3 = j.split(',')
            self.filenames.append(temp1)
            self.url.append(temp2)
            self.crlaliaslist.append(temp3)
        self.filenames = [x.strip() for x in self.filenames]
        k = 0
        count, count1, pollerror = 0, 0, 0

        for i in self.filenames:
            v1 = i
            url = 'https://' + str(appliance) + '/rest/certificates/ca/' + str(self.crlaliaslist[k]) + '/crl'
            headers = {'Auth': self.sessionid,
                       'X-Api-Version': '600', 'Accept': 'application/json'}
            f = open('crls/' + v1, 'rb')
            files = {'file': ('file', f)}
            flag = 0
            error = ''
            thread_helper.stat1 = 1
            thread_helper.msg = 'Uploading CRL against certificate with aliasname ' + \
                                str(self.crlaliaslist[k]).strip('\n') + "...."
            thread = thread_helper.myTimeThread()
            thread.daemon = True
            thread.start()
            for j in range(int(maxuploadtries)):
                socket.setdefaulttimeout(int(maxtime))
                try:
                    if self.proxyurl == []:
                        response = requests.put(url, files=files, headers=headers, verify=False,
                                                timeout=int(uploadtimeout))
                    else:
                        proxies = {'http': self.proxyurl}
                        response = requests.put(url, files=files, headers=headers, verify=False, proxies=proxies,
                                                timeout=int(uploadtimeout))
                    flag = 0
                    break
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    error = e
                    flag = 1
                    continue
                except (requests.exceptions.HTTPError, requests.exceptions.RequestException) as e:
                    error = e
                    flag = 1
                    break
                except timeout as e:
                    error = e
                    flag = 1
                    continue
                except Exception as e:
                    error = e
                    flag = 2
                    break

            if flag == 1:
                log.error("%s, %s while uploading %s to appliance.Check for network or proxy issues "
                          % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), error, self.crlaliaslist[k]))
                continue

            if flag == 2:
                log.error("%s, %s while uploading %s to appliance "
                          % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), error, self.crlaliaslist[k]))
                continue

            resp = json.loads(response.text)
            if int(response.status_code) == 202:
                pollerror = pollerror + self.getresp(resp, appliance, self.crlaliaslist[k], self.proxyurl, i)
                thread_helper.stat1 = 0
            else:
                thread_helper.stat1 = 0
                if resp['errorCode'] == 'Cert.CRL_DUPLICATE_ERROR':
                    count1 = count1 + 1
                    log.info('%s, Skipping upload of the CRL %s against the certificate with aliasname %s to appliance '
                             'as the same CRL is already present in the appliance' % (strftime("%Y-%m-%d %H:%M:%S UTC",
                                                                                               gmtime()), i, str(self.crlaliaslist[k].strip('\n'))))
                    print("\nSkipped upload of CRL against certificate with aliasname %s. See logs for details"
                          % str(self.crlaliaslist[k]).strip('\n'), end='')
                elif resp['errorCode'] == 'Cert.CRL_OUTDATED_CRL_ERROR':
                    count1 = count1 + 1
                    log.info(
                        '%s, Skipping upload of the CRL %s against the certificate with aliasname %s to appliance as a '
                        'never CRL is already present in the appliance' % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()),
                                                                           i, str(self.crlaliaslist[k].strip('\n'))))
                    print("\nSkipped upload of CRL against certificate with aliasname %s. See logs for details"
                          % str(self.crlaliaslist[k]).strip('\n'), end='')

                else:
                    count = count + 1
                    log.error("%s, Error code is %s error message is %s error details is %s recommended action is %s"
                              " while validating CRL %s against the certificate with aliasname %s "
                              % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), str(resp['errorCode']), str(resp['message']),
                                 str(resp['details']), str(resp['recommendedActions'][0]), i, str(self.crlaliaslist[k].strip('\n'))))
                    print("\nFailed to upload CRL against certificate with aliasname %s. See logs for details"
                          % str(self.crlaliaslist[k]).strip('\n'), end='')
            k = k + 1
            time.sleep(1)
        thread_helper.stat1 = 0
        if (len(self.crlaliaslist) - count - count1) != 0:
            print("\nUploaded %s CRLs to appliance" % (len(self.crlaliaslist) - count - count1), end='')
            log.info('%s,Uploaded %s CRLs to appliance'
                     % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), (len(self.crlaliaslist) - count - count1)))
        if count != 0 or int(pollerror) != 0:
            print("\nFailed to upload %s CRLs to appliance" % (count+int(pollerror)), end='')
            log.info('%s, Failed to upload %s CRLs to appliance' % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()),
                                                                    (count+int(pollerror))))
        if count1 != 0:
            print("\nSkipped upload of %s CRLs to appliance" % count1, end='')
            log.info(
                '%s, Skipped upload of %s CRLs to appliance' % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), count1))
        f.close()
        if os.path.isdir('crls'):
            shutil.rmtree('crls')
        crl_download.logout(appliance, sessionid, proxyurl)

    def getresp(self, task, applianceid, crlname, proxyurl, i):
        count, flag = 0, 0
        timestart = time.time()
        timekeep = 0
        while int(task['percentComplete']) < 100 and count < int(polltries) and timekeep < int(polltime):
            timewatch = time.time()
            url = 'https://' + applianceid + task['uri']
            if proxyurl == '':
                proxy_handler = urllib.request.ProxyHandler({})
            else:
                proxies = {"http": proxyurl}
                proxy_handler = urllib.request.ProxyHandler(proxies)
            try:
                opener = urllib.request.build_opener(proxy_handler)
                urllib.request.install_opener(opener)
                socket.setdefaulttimeout(int(maxtime))
                request = urllib.request.Request(url)
                gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
                request.add_header('X-API-Version', '600')
                request.add_header('Auth', self.sessionid)
                request.get_method = lambda: 'GET'
                response = urllib.request.urlopen(request, context=gcontext,timeout=int(maxrestreadtime))
                resp = response.read().decode('utf8')
                task = json.loads(resp)

            except timeout as e:
                count = count + 1
                flag = 1
                timekeep = timekeep + int(time.time())
                continue

            except (urllib.request.URLError, urllib.request.HTTPError) as e:
                count = count + 1
                timekeep = timekeep + int(time.time())
                continue

            except Exception as e:
                log.error("%s ,Unexpected error %s occurred while polling for %s upload against the certificate with "
                          "aliasname %s" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e, i, crlname.strip('\n')))
                return 1

            timekeep = timekeep + int(time.time() - timewatch)
        timeend = time.time()
        if count >= int(polltries) and flag == 0:
            thread_helper.stat1 = 0
            log.error(
                "%s ,Error while polling for %s upload against the certificate with aliasname %s. Check for network or "
                "proxy issues" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), i, crlname.strip('\n')))
            print("\nCould not poll for CRL upload against certificate with aliasname %s. See logs for details"
                  % crlname.strip('\n'), end='')
            return 0
        if count >= int(polltries) and flag == 1:
            thread_helper.stat1 = 0
            log.error(
                "%s ,Timeout Error while polling for %s upload against the certificate with aliasname %s. Check for "
                "network or proxy issues" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), i, crlname.strip('\n')))
            print("\nCould not poll for CRL upload against certificate with aliasname %s. See logs for details"
                  % crlname.strip('\n'), end='')
            return 0
        if task['taskErrors']:
            thread_helper.stat1 = 0
            log.error("%s, Error %s while uploading CRL %s against the certificate with aliasname %s "
                      % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), task['taskErrors'], i, crlname.strip('\n')))
            print("\nFailed to upload CRL against certificate with aliasname %s. See logs for details"
                  % crlname.strip('\n'), end='')
            return 1
        else:
            thread_helper.stat1 = 0
            log.info(
                "%s, Successfully uploaded the CRL %s against the certificate with aliasname %s to appliance in %s "
                "seconds" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), i, crlname.strip('\n'),
                             str(round(timeend - timestart, 2))))
            print("\nUploaded CRL against the certificate with aliasname %s" % crlname.strip('\n'), end='')
            return 0
