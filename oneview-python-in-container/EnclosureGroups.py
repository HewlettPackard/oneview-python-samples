# -*- coding: utf-8 -*-
###
# Copyright (2018) Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

import logging

from pprint import pprint
from hpOneView.oneview_client import OneViewClient
from hpOneView.exceptions import HPOneViewException

CONFIG = {
    "api_version": 600,
    "ip": "127.0.0.1",
    "credentials": {
        "userName": "administrator",
        "password": "admin"
    }
}

# Initiate a connection to the appliance and instanciate a new OneViewClient class object
ONEVIEW_CLIENT = OneViewClient(CONFIG)

# Get all enclosure groups
print("Get list of all enclosure groups\n")
ALL_ENCLOSURE_GROUPS = ONEVIEW_CLIENT.enclosure_groups.get_all()
pprint(ALL_ENCLOSURE_GROUPS)
