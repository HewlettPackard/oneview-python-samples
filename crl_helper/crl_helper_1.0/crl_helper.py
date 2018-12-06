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

import crl_download
import argparse
import urllib.request
import os
import shutil
import signal
import socket
import sys
import logging
import ssl
import json
import getpass
from time import strftime, gmtime
from socket import timeout
from crl_validate_and_upload import validateCrl
import thread_helper
from gettext import gettext as _

logging.basicConfig(filename="crl_helper.log", level=logging.DEBUG)
log = logging.getLogger(__name__)
stat = 1
separator = "="
keys = {}
with open('download_crl.properties') as f:
    for line in f:
        if separator in line:
            name, value = line.split(separator, 1)
            keys[name.strip()] = value.strip()

maxlogintries = keys['appliance.login.retries']
maxresttime = keys['appliance.rest.connection.timeout']
maxconnecttime=keys['appliance.rest.read.timeout']


class Myparser(argparse.ArgumentParser):

    def exit(self, status=0, message=None):
        if message:
            self._print_message(message + '\n', sys.stderr)
            self.print_usage(sys.stderr)
        sys.exit(status)

    def error(self, message):
        args = {'prog': self.prog, 'message': message}
        self.exit(2, _('%(prog)s: error: %(message)s\n') % args)


class downloadAndVerifyCrl:

    def __init__(self):
        parser = Myparser(add_help=False, usage=self.msg())
        requiredNamed = parser.add_argument_group('Required arguments')
        requiredNamed.add_argument('-appliance', help='Appliance IP address or name', required='True')
        requiredNamed.add_argument('-username', help='Appliance Username', required='True')
        optional = parser.add_argument_group('optional arguments')
        optional.add_argument('-password', help='Appliance password')
        optional.add_argument("-help", action="help", help="show this help message and exit")
        optional.add_argument('-proxy', help='Proxy address if required', default='', dest='proxyurl')

        args = vars(parser.parse_args())

        self.applianceip = args['appliance']
        self.username = args['username']
        self.password = args['password']
        self.proxyurl = args['proxyurl']
        self.sessionid = ''
        self.advanced = 'No'
        if self.password is None:
            try:
                self.password = getpass.getpass("Enter Appliance password:")
            except KeyboardInterrupt:
                log.info("%s, User interrupted the execution (Keyboard Interrupt)"
                          % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime())))
                return
            except Exception as e:
                log.error("%s, Error is %s" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e))
                return

        if self.password is None:
            print("\nNo password entered", end='')
            log.error("%s,No password was entered. Please provide a password"
                      % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime())))
            return

        if not (self.advanced == 'Yes' or self.advanced == 'No'):
            print("\nInvalid advanced option entered. Please provide (Yes/No)", end='')
            log.error("%s,Invalid advanced option entered --> %s." % (
                strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), self.advanced))
            return

        if os.path.isfile('crlfilename.txt'):
            try:
                os.remove('crlfilename.txt')
            except (OSError, Exception) as e:
                log.error("%s, %s while deleting the existing file crlfilename.txt"
                          % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e))
                return

        if os.path.isdir('crls'):
            try:
                shutil.rmtree('crls')
            except Exception as e:
                log.error("%s, %s while deleting the existing crls directory"
                          % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), e))
                return

        print("----------Script progress summary printed below. For details see crl_helper.log----------", end='')
        print("\nConnecting to appliance at %s" % self.applianceip, end='')
        self.thread1 = thread_helper.myThread()
        self.thread1.start()
        signal.signal(signal.SIGINT, self.signal_handler)

        response, self.sessionid = self.checkpermissions()
        if response == []:
            print("\nUnable to fetch user permissions", end='')
            log.error("%s, Unable to fetch user permissions for appliance %s." % (
                strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), self.applianceip))
            return
        if not response:
            return
        response = crl_download.dwd(self.applianceip, self.proxyurl,
                                          self.sessionid)

        if response == []:
            print("\nNo CRL files downloaded", end='')
            log.error("%s, No CRL files downloaded for verification" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime())))
            print("\nNo CRL files uploaded to appliance", end='')
            log.error("%s, No CRL files uploaded to appliance" % (strftime("%Y-%m-%d %H:%M:%S UTC", gmtime())))
            crl_download.logout(self.applianceip, self.sessionid, self.proxyurl)
            return

        validateAndUploadCrl = validateCrl()
        validateAndUploadCrl.validateAndUpload(response, self.applianceip, self.proxyurl,
                                      self.sessionid)

    def msg(self):

        return 'crl_helper.py -appliance APPLIANCE -username USERNAME [-password PASSWORD] ' \
               '[-help] [-proxy PROXYURL]\n\n'\
               'example 1: python crl_helper.py -appliance 10.20.30.40 -username administrator -password admin\n' \
               'example 2: python crl_helper.py -appliance oneview.mycompany.com -username administrator -password ' \
               'admin\n' \
               'example 3: python crl_helper.py -appliance oneview.mycompany.com -username administrator -password ' \
               'admin -proxy http://web-proxy.mycompany.com:8080\n' \
               'example 4: python crl_helper.py -appliance oneview.mycompany.com -username administrator -password ' \
               'admin -proxy http://proxyuser:proxypassword@web-proxy.myconmpany.com:8080\n' \
               'example 5: python crl_helper.py -appliance oneview.mycompany.com -username administrator [ User will be'\
               ' prompted for password ] Enter Appliance password:\n' \
               'example 6: python crl_helper.py -appliance oneview.mycompany.com -username administrator'\
               ' -proxy http://web-proxy.mycompany.com:8080 [ User will be prompted for password ]' \
               ' Enter Appliance password:\n'


    def signal_handler(self, sig, frame):

        thread_helper.stat = 0
        log.info(
            "%s, User interrupted the execution (Keyboard Interrupt)" % strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()))
        if self.sessionid:
            crl_download.logout(self.applianceip, self.sessionid, self.proxyurl)
        sys.exit(0)

    def checkpermissions(self):
        url = 'https://' + self.applianceip + '/rest/users'
        sessionid = ''
        sessionid = crl_download.login(self.applianceip, self.username, self.password, self.proxyurl, 0)
        if sessionid == '':
            log.error("%s, Unable to login to appliance %s.Tried %s times.Check login credentials" % (
                strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), self.applianceip, maxlogintries))
            return False, sessionid
        elif sessionid == 1:
            return False, sessionid
        else:
            print('\nSuccessfully logged into appliance %s' % self.applianceip, end='')
            log.info("%s, Successfully logged into appliance %s " % (
                strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), self.applianceip))

            if self.proxyurl == '':
                proxy_handler = urllib.request.ProxyHandler({})
            else:
                proxies = {"http": self.proxyurl}
                proxy_handler = urllib.request.ProxyHandler(proxies)
            count, flag = 0, 0
            error = ''
            while count < int(maxlogintries):
                try:
                    opener = urllib.request.build_opener(proxy_handler)
                    urllib.request.install_opener(opener)
                    request = urllib.request.Request(url)
                    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
                    request.add_header('X-API-Version', '600')
                    request.add_header('Auth', sessionid)
                    request.get_method = lambda: 'GET'
                    socket.setdefaulttimeout(int(maxresttime))
                    response = urllib.request.urlopen(request, context=gcontext, timeout=int(maxconnecttime))
                    resp1 = response.read().decode('utf8')
                    resp = json.loads(resp1)
                    for i in range(int(resp['count'])):
                        if (resp['members'][i]['userName'].lower() == self.username.lower() and
                                resp['members'][i]['permissions'][0]['roleName'] == 'Infrastructure administrator'):
                            log.info("%s, User %s is an infrastructure administrator and can upload CRLs" % (
                                strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), self.username))
                            return True, sessionid
                    print(
                        "\nUser %s is not an infrastructure administrator and can't upload CRLs" % (
                            self.username), end='')
                    log.info("%s, User %s is not an infrastructure administrator and can't upload CRLs. Only "
                             "infrastructure administrator can upload CRLs" % (strftime("%Y-%m-%d %H:%M:%S UTC",
                                                                                        gmtime()), self.username))
                    return False, sessionid

                except timeout as e:
                    error = e
                    flag = 3
                    count = count + 1
                    continue

                except urllib.error.HTTPError as e:
                    count = count + 1
                    error = e
                    flag = 1
                    break

                except urllib.error.URLError as e:
                    count = count+1
                    error = e
                    flag = 1
                    if not isinstance(error.reason, timeout):
                        break
                    continue

                except TimeoutError as e:
                    error = e
                    count = count + 1
                    flag = 2
                    continue

            if flag == 1:
                print("\nUnable to fetch user roles", end='')
                log.error("%s, %s while fetching user roles. Check for bad URLs " % (
                    strftime("%Y-%m-%d %H:%M:%S UTC", gmtime()), error))
                return False, sessionid

            if flag == 2 or flag == 3:
                print('\nTimeout while fetching user roles', end='')
                log.error("%s, Timeout while fetching user roles.Check for network connection and proxy settings" % (
                    strftime("%Y-%m-%d %H:%M:%S UTC", gmtime())))
                return False, sessionid


n1 = downloadAndVerifyCrl()
thread_helper.stat = 0
