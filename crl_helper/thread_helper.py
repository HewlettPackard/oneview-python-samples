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

stat = 1
stat1 = 1
msg = ''

class myThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while stat == 1:
            print(".", end='')
            sys.stdout.flush()
            time.sleep(0.5)


class myTimeThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        count = 0
        print('\n', end='\r')
        while stat1 == 1:
            print("%s %d secs" % (msg, count), end='\r')
            time.sleep(1)
            count = count + 1


class myTimeThread1(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        count = 0
        print('\n', end='\r')
        while stat1 == 1:
            print("%s %.2f secs" % (msg, count), end='\r')
            time.sleep(0.5)
            count = count + 0.5

