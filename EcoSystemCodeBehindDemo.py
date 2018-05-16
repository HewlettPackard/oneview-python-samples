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

from pprint import pprint
from hpOneView.oneview_client import OneViewClient
from hpOneView.exceptions import HPOneViewException

CONFIG = {
    "api_version": 500,
    "ip": "hpov7.doctors-lab.local",
    "credentials": {
        "userName": "administrator",
        "password": "hpinvent"
    }
}

# Initiate a connection to the appliance and instanciate a new OneViewClient class object
ONEVIEW_CLIENT = OneViewClient(CONFIG)

# These variables must be defined according with your environment
SERVER_PROFILE_TEMPLATE_NAME = "Big Data Node Template v1"
SERVER_PROFILE_NAME = "Prod-Swift-01"
SERVER_PROFILE_TEMPLATE_DESCRIPTION = "Corp standard big data node, version 1.0"

# Get infrastrucutre resource objects
ENCLOSURE_GROUP_OBJ = ONEVIEW_CLIENT.enclosure_groups.get_by('name', 'DCS Synergy Default EG')
SERVER_HARDWARE_TYPE_OBJ = ONEVIEW_CLIENT.server_hardware_types.get_by('name', 'SY 480 Gen10 1')
FIRMWARE_BUNDLE_OBJ = ONEVIEW_CLIENT.firmware_drivers.get_by('isoFileName', 'SPP_2017_10_20171215_for_HPE_Synergy_Z7550-96455.iso')
ETHERNET_NETWORK_OBJ = ONEVIEW_CLIENT.ethernet_networks.get_by('name', 'Management Network (VLAN1)')
NETWORK_SET_OBJ = ONEVIEW_CLIENT.network_sets.get_by('name', 'Prod NetSet')
FABRICA_NETWORK_OBJ = ONEVIEW_CLIENT.fc_networks.get_by('name', 'Prod Fabric A')
FABRICB_NETWORK_OBJ = ONEVIEW_CLIENT.fc_networks.get_by('name', 'Prod Fabric B')

# Define firmware policy
FIRMWARE = dict(
    manageFirmware=True,
    forceInstallFirmware=False,
    firmwareInstallType = "FirmwareAndOSDrivers",
    firmwareBaselineUri = FIRMWARE_BUNDLE_OBJ[0]["uri"],
    firmwareActivationType = "Immediate"
)

# Define connections
CONNECTIONS = dict(
    manageConnections = True,
    connections = [
        dict(
            id=1,
            name="Con1",
            functionType="Ethernet",
            networkUri=ETHERNET_NETWORK_OBJ[0]["uri"],
            portId="Auto",
            requestedVFs=0,
            requestedMbps=5000,
            boot=dict(
                priority="NotBootable"
            )
        ),
        dict(
            id=2,
            name="Con2",
            functionType="Ethernet",
            networkUri=ETHERNET_NETWORK_OBJ[0]["uri"],
            portId="Auto",
            requestedVFs=0,
            requestedMbps=5000,
            boot=dict(
                priority="NotBootable"
            )
        )
    ]    
)

# Attach D3940 DAS JBOD storage
LOCAL_STORAGE = dict(
    sasLogicalJBODs = [
        dict(
            id = 1,
            deviceSlot = "Mezz 1",
            name = "Data Volume 1",
            numPhysicalDrives = 2,
            driveMinSizeGB = 500,
            driveMaxSizeGB = 500,
            driveTechnology = "SataHdd"
        )
    ],
    controllers = [
        dict(
            logicalDrives = [],
            deviceSlot = "Mezz 1",
            mode = "Mixed",
            initialize = True
        )
    ]
)

# Set boot mode to managed, UEFI Optimized and BIOS settings
BOOT_MODE = dict(
    manageMode = True,
    mode = 'UEFIOptimized',
    pxeBootPolicy = 'IPv4'
)
BOOT_CONFIG = dict(
    manageBoot = True,
    order = [
        "HardDisk"
    ]
)
BIOS_BOOT_SETTINGS = dict(
    manageBios = True,
    overriddenSettings = [
        dict(id = "MemPatrolScrubbing", value = "Disabled"),
        dict(id = "CustomPostMessage", value = "Compsable EcoSystem is AWESOME!"),
        dict(id = "CollabPowerControl", value = "Disabled"),
        dict(id = "WorkloadProfile", value = "LowLatency"),
        dict(id = "EnergyPerfBias", value = "MaxPerf"),
        dict(id = "EnergyEfficientTurbo", value = "Disabled"),
        dict(id = "ProcVirtualization", value = "Disabled"),
        dict(id = "Sriov", value = "Disabled"),
        dict(id = "IntelProcVtd", value = "Disabled"),
        dict(id = "MinProcIdlePkgState", value = "NoState"),
        dict(id = "ProcTurbo", value = "Disabled"),
        dict(id = "PowerRegulator", value = "StaticHighPerf"),
        dict(id = "ProcX2Apic", value = "Disabled"),
        dict(id = "UncoreFreqScaling", value = "Maximum"),
        dict(id = "IntelUpiPowerManagement", value = "Disabled"),
        dict(id = "NumaGroupSizeOpt", value = "Clustered"),
        dict(id = "MinProcIdlePower", value = "NoCStates")
    ]
)

# Create a server profile template
print("\nCreate '%s' Server Profile Template" % SERVER_PROFILE_TEMPLATE_NAME)
TEMPLATE_OPTIONS = dict(
    name = SERVER_PROFILE_TEMPLATE_NAME,
    description = SERVER_PROFILE_TEMPLATE_DESCRIPTION,
    serverHardwareTypeUri = SERVER_HARDWARE_TYPE_OBJ[0]["uri"],
    enclosureGroupUri = ENCLOSURE_GROUP_OBJ[0]["uri"],
    firmware = FIRMWARE,
    connectionSettings = CONNECTIONS,
    localStorage = LOCAL_STORAGE,
    bootMode = BOOT_MODE,
    boot = BOOT_CONFIG,
    bios = BIOS_BOOT_SETTINGS,
    hideUnusedFlexNics = True
)
CREATE_TEMPLATE_RESULTS = ONEVIEW_CLIENT.server_profile_templates.create(TEMPLATE_OPTIONS)
# pprint(CREATE_TEMPLATE_RESULTS)

# Get all
print("\nGet list of all server profile templates")
ALL_SERVER_PROFILE_TEMPLATES = ONEVIEW_CLIENT.server_profile_templates.get_all()
for SERVER_PROFILE_TEMPLATE_OBJ in ALL_SERVER_PROFILE_TEMPLATES:
    print('  %s' % SERVER_PROFILE_TEMPLATE_OBJ['name'])

# Get by name
# print("\nGet a server profile templates by name")
# SERVER_PROFILE_TEMPLATE_OBJ = ONEVIEW_CLIENT.server_profile_templates.get_by_name(SERVER_PROFILE_TEMPLATE_NAME)
# pprint(SERVER_PROFILE_TEMPLATE_OBJ)

# Get new profile
print("\nGet new profile object from API")
SERVER_PROFILE_OBJ = ONEVIEW_CLIENT.server_profile_templates.get_new_profile(SERVER_PROFILE_TEMPLATE_OBJ["uri"])

# Get server hardware resource
SERVER_HARDWARE_RESOURCES = ONEVIEW_CLIENT.server_hardware.get_by('serverHardwareTypeUri', SERVER_HARDWARE_TYPE_OBJ[0]["uri"])

# Get first server that matches the criteria
print("\nGet available server hardware that matches criteria")
SERVER_HARDWARE_OBJ = next((server for server in SERVER_HARDWARE_RESOURCES if (server["serverProfileUri"] == None and (server["processorCount"] * server["processorCoreCount"]) >= 4 and server["memoryMb"] >= (512 * 1024))), None)
print('  %s' % SERVER_HARDWARE_OBJ['name'])

if SERVER_HARDWARE_OBJ != None:
    SERVER_PROFILE_OBJ["serverHardwareUri"] = SERVER_HARDWARE_OBJ["uri"]
    SERVER_PROFILE_OBJ["name"] = SERVER_PROFILE_NAME

    # Poweroff the server if needed
    if SERVER_HARDWARE_OBJ["powerState"] != "Off":

        print("\nWill power off '%s' server" % SERVER_HARDWARE_OBJ["name"])

        try:
            configuration = {
                "powerState": "Off",
                "powerControl": "MomentaryPress"
            }
            server_power = ONEVIEW_CLIENT.server_hardware.update_power_state(configuration, SERVER_HARDWARE_OBJ["uuid"])
            print("\nSuccessfully changed the power state of server '{name}' to '{powerState}'".format(**server_power))
        except HPOneViewException as e:
            print(e.msg)

    else:
        print("\nServer already powered off.")

    # Create the Server Profile resource assigned to the specific server hardware resource
    print("\nCreating Server Profile resource")
    ASYNC_TASK_OBJ = ONEVIEW_CLIENT.server_profiles.create(SERVER_PROFILE_OBJ)

    print("\nAsync Task Uri: %s" % ASYNC_TASK_OBJ["uri"])

else:
    print("\nNo server found with the criteria. Ending.")

print("\nDone.")