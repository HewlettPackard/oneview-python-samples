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
from pprint import pprint
import json
import copy

from hpOneView.exceptions import HPOneViewException
from hpOneView.oneview_client import OneViewClient

TABSPACE         = "    "
COMMA           = ','
CR              = '\n'


CONFIG = {
    "api_version": 500,
    "ip": "192.168.1.51",
    "credentials": {
        "userName": "administrator",
        "password": "password"
    }
}

    

def format_option(optionName,optionValue,indentlevel=0,endDict=',',useQuote=True):
    TABSPACE         = indentlevel * "    "
    format_str      = TABSPACE
    if optionValue is not None:
        if isinstance(optionValue,int):
            format_str += "{0:30} = {1:d} {2}"
        else:
            format_str += "{0:30} = \"{1:s}\" {2}"
            if not useQuote:
                format_str = format_str.replace("\"", "")
            
    return format_str.format(optionName,optionValue,endDict)




def build_netUri(networkType,nativeNetworkUri):
    if 'Ethernet' == networkType:
        _net                =  oneview_client.ethernet_networks.get(nativeNetworkUri)
        net_name            = _net['name']
        net_uri             = "oneview_client.ethernet_networks.get_by(\'name\', \'{0}\')[0][\'uri\']".format(net_name)
    else:
        _net                =  oneview_client.fc_networks.get(nativeNetworkUri)
        net_name            = _net['name']
        net_uri             = "oneview_client.fc_networks.get_by(\'name\', \'{0}\')[0][\'uri\']".format(net_name)
    return net_uri

def build_uri(sourceUri):
    dest_uri                 = ""

    if '/os-deployment-plans' in sourceUri:
        res                 = oneview_client.os_deployment_plans.get(sourceUri)
        res_name            = res['name']
        dest_uri            = "oneview_client.os_deployment_plans.get_by(\'name\', \'{0}\')[0][\'uri\']".format(res_name)
    if '/enclosure-groups' in sourceUri:
        res                 = oneview_client.enclosure_groups.get(sourceUri)
        res_name            = res['name']
        dest_uri            = "oneview_client.enclosure_groups.get_by(\'name\', \'{0}\')[0][\'uri\']".format(res_name)
    if '/logical-interconnect-groups' in sourceUri:
        res                 = oneview_client.logical_interconnect_groups.get(sourceUri)
        res_name            = res['name']
        dest_uri            = "oneview_client.logical_interconnect_groups.get_by(\'name\', \'{0}\')[0][\'uri\']".format(res_name)
    if '/sas-logical-interconnect-groups' in sourceUri:
        res                 = oneview_client.sas_logical_interconnect_groups.get(sourceUri)
        res_name            = res['name']
        dest_uri            = "oneview_client.sas_logical_interconnect_groups.get_by(\'name\', \'{0}\')[0][\'uri\']".format(res_name)
    if '/ethernet-networks' in sourceUri:
        res                 = oneview_client.ethernet_networks.get(sourceUri)
        res_name            = res['name']
        dest_uri            = "oneview_client.ethernet_networks.get_by(\'name\', \'{0}\')[0][\'uri\']".format(res_name)
    if '/fc-networks' in sourceUri:
        res                 = oneview_client.fc_networks.get(sourceUri)
        res_name            = res['name']
        dest_uri            = "oneview_client.fc_networks.get_by(\'name\', \'{0}\')[0][\'uri\']".format(res_name)
    if '/network-sets' in sourceUri:
        res                 = oneview_client.network_sets.get(sourceUri)
        res_name            = res['name']
        dest_uri            = "oneview_client.network_sets.get_by(\'name\', \'{0}\')[0][\'uri\']".format(res_name)
    if '/fcoe-networks' in sourceUri:
        res                 = oneview_client.fcoe_networks.get(sourceUri)
        res_name            = res['name']
        dest_uri            = "oneview_client.fcoe_networks.get_by(\'name\', \'{0}\')[0][\'uri\']".format(res_name)
 
   
    return dest_uri

# ================================================================================================
#
#   Build import libraries
#
# ================================================================================================
def build_import_files(scriptCode):

    scriptCode.append("#===================Import section ========================"                                                                 )
    scriptCode.append("from pprint import pprint"                                                                                                   )
    scriptCode.append("import json"                                                                                                                 )
    scriptCode.append("import copy"                                                                                                                 )

    scriptCode.append("from hpOneView.exceptions import HPOneViewException"                                                                         )
    scriptCode.append("from hpOneView.oneview_client import OneViewClient"                                                                          )

    scriptCode.append(CR)
# ================================================================================================
#
#   Build constants
#
# ================================================================================================
def build_constants(scriptCode):
    scriptCode.append("TABSPACE                                     = \'    \'"                                                 )    
    scriptCode.append("COMMA                                        = \',\'"                                                    )
    scriptCode.append("CR                                           = \'\\n\'"                                                  )  
    scriptCode.append(CR)                        

# ================================================================================================
#
#   Build config.json and OV connection
#
# ================================================================================================
def build_config(scriptCode):

    
    scriptCode.append(CR)
    scriptCode.append(CR)
    scriptCode.append("#===================Config json ========================"                                                                    )       
    scriptCode.append("CONFIG                                       =     {"                                                                         )
    scriptCode.append("     \'api_version\'                           : 800"                                                          )
    scriptCode.append("     \'ip\'                                    : \'<destination_OV_name_ip>\'"                                 )
    scriptCode.append("     \'credentials\'                           : {"                                 )
    scriptCode.append("             \'userName\'                      : \'<destination_OV_admin_name>\'  "                            )
    scriptCode.append("             \'password\'                      : \'<destination_OV_admin_pwd>\'  "                             )
    scriptCode.append("     } "                                                                                                                     )
    scriptCode.append("} "                                                                                                                          )

    scriptCode.append("oneview_client                                = OneViewClient(CONFIG)"                                            )
    scriptCode.append(CR)
    scriptCode.append(CR)


# ================================================================================================
#
#   Write to file
#
# ================================================================================================
def write_to_file(scriptCode, filename):
    file                        = open(filename, "w")
    code                        = CR.join(scriptCode)
    file.write(code)

    file.close()


# ================================================================================================
#
#   generate_ethernet_networks_script
#
# ================================================================================================
def generate_ethernet_networks_script(to_file):
    scriptCode = []
    build_import_files(scriptCode)
    build_constants(scriptCode)
    build_config(scriptCode)
    
    ethernet_nets = oneview_client.ethernet_networks.get_all()

    for net in ethernet_nets:
        name                    = net["name"]
        description             = net["description"]
        purpose                 = net["purpose"]
        etherType               = net["ethernetNetworkType"]
        vlanId                  = net["vlanId"]
        smartLink               = net["smartLink"]
        privateNetwork          = net["privateNetwork"]
        connectionTemplateUri   = net['connectionTemplateUri']
        ethernetNetworkType     = net['ethernetNetworkType']


        scriptCode.append(CR)
        scriptCode.append("#===================Attributes for network {} ========================".format(name)                                         )

        scriptCode.append("ETHERNET_NETWORK                                             = dict()"                                                       )
        scriptCode.append("ETHERNET_NETWORK.update(name                                 = \'{}\')".format(name)                                         )
        if description is not None:
            scriptCode.append("ETHERNET_NETWORK.update(description                          = \'{}\')".format(description)                              )
        scriptCode.append("ETHERNET_NETWORK.update(purpose                              = \'{}\')".format(purpose)                                      )
        scriptCode.append("ETHERNET_NETWORK.update(ethernetNetworkType                  = \'{}\')".format(ethernetNetworkType)                          )

        if etherType == 'Tagged':
            scriptCode.append("ETHERNET_NETWORK.update(vlanId                               = {})".format(description)                                  )
        
        scriptCode.append("ETHERNET_NETWORK.update(smartLink                            = \'{}\')".format(smartLink)                                    )
        scriptCode.append("ETHERNET_NETWORK.update(privateNetwork                       = \'{}\')".format(privateNetwork)                               )


        con_template = oneview_client.connection_templates.get(connectionTemplateUri)
        bandwidth    = con_template['bandwidth']
        tBandwidth   = bandwidth['typicalBandwidth']
        mBandwidth   = bandwidth['maximumBandwidth']



        scriptCode.append("# Create Ethernet network {}".format(name)                                                                                   )
        scriptCode.append("net                      = oneview_client.ethernet_networks.create(ETHERNET_NETWORK)"                                        )
        scriptCode.append("con_template             = oneview_client.connection_templates.get(net[\'connectionTemplateUri\'])"                          )
        scriptCode.append("con_template[\'bandwidth\'][\'typicalBandwidth\']             = \'{}\')".format(tBandwidth)                                  )
        scriptCode.append("con_template[\'bandwidth\'][\'maximumBandwidth\']             = \'{}\')".format(mBandwidth)                                  )
        scriptCode.append("con_template_updated     = oneview_client.connection_templates.update(con_template)"                                         )

    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)


# ================================================================================================
#
#   generate_fc_networks_script
#
# ================================================================================================
def generate_fc_networks_script(to_file):
    scriptCode   = []
    build_import_files(scriptCode)
    build_constants(scriptCode)
    build_config(scriptCode)
    
    fc_nets = oneview_client.fc_networks.get_all()

    for net in fc_nets:
        name                    = net["name"]
        description             = net["description"]
        fabricType              = net["fabricType"]
        autoLoginRedistribution = net["autoLoginRedistribution"]
        linkStabilityTime       = net["linkStabilityTime"]
        managedSanUri           = net["managedSanUri"]
        connectionTemplateUri   = net['connectionTemplateUri']

        

        scriptCode.append(CR)
        scriptCode.append("#===================Attributes for network {} ========================".format(name)                                         )

        scriptCode.append("FC_NETWORK                                                   = dict()"                                                       )
        scriptCode.append("FC_NETWORK.update(name                                       = \'{}\')".format(name)                                         )
        if description is not None:
            scriptCode.append("FC_NETWORK.update(description                                = \'{}\')".format(description)                              )

        scriptCode.append("FC_NETWORK.update(fabricType                                 = \'{}\')".format(fabricType)                                   )
        scriptCode.append("FC_NETWORK.update(autoLoginRedistribution                    = \'{}\')".format(autoLoginRedistribution)                      )
        scriptCode.append("FC_NETWORK.update(linkStabilityTime                          = \'{}\')".format(linkStabilityTime)                            )


        # TBD - Also make sure thate endDict is here
        # if managedSanUri is not None:
        #    scriptCode.append("FC_NETWORK.update(managedSanUri= \'{}\')".format(managedSanUri))
        


        
        con_template = oneview_client.connection_templates.get(connectionTemplateUri)
        bandwidth    = con_template['bandwidth']
        tBandwidth   = bandwidth['typicalBandwidth']
        mBandwidth   = bandwidth['maximumBandwidth']



        scriptCode.append("# Create FC network {}".format(name)                                                                                         )
        scriptCode.append("net                      = oneview_client.fc_networks.create(FC_NETWORK)"                                                    )
        scriptCode.append("con_template             = oneview_client.connection_templates.get(net[\'connectionTemplateUri\'])"                          )
        scriptCode.append("con_template[\'bandwidth\'][\'typicalBandwidth\']             = \'{}\')".format(tBandwidth)                                  )
        scriptCode.append("con_template[\'bandwidth\'][\'maximumBandwidth\']             = \'{}\')".format(mBandwidth)                                  )
        scriptCode.append("con_template_updated     = oneview_client.connection_templates.update(con_template)"                                         )


    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)

# ================================================================================================
#
#   generate_fcoe_networks_script
#
# ================================================================================================
def generate_fcoe_networks_script(to_file):
    scriptCode   = []
    build_import_files(scriptCode)
    build_constants(scriptCode)
    build_config(scriptCode)
    
    fcoe_nets       = oneview_client.fcoe_networks.get_all()

    for net in fcoe_nets:
        name                    = net["name"]
        description             = net["description"]
        vlanId                  = net["vlanId"]
        fabricUri               = net["fabricUri"]
        managedSanUri           = net["managedSanUri"]
        connectionTemplateUri   = net['connectionTemplateUri']

        scriptCode.append(CR)
        scriptCode.append("#===================Attributes for network {} ========================".format(name)                                         )

        scriptCode.append("FCOE_NETWORK                                                 = dict()"                                                       )
        scriptCode.append("FCOE_NETWORK.update(name                                     = \'{}\')".format(name)                                         )
        if description is not None:
            scriptCode.append("FCOE_NETWORK.update(description                              = \'{}\')".format(description)                              )

        scriptCode.append("FCOE_NETWORK.update(vlanId                                   = {})".format(vlanId)                                           )

        # TBD - Also make sure thate endDict is here
        # if fabricUri is not None:
        #    scriptCode.append("FCOE_NETWORK.update(fabricUri    = \'{}\')".format(fabricUri))
        # if managedSanUri is not None:
        #    scriptCode.append("FCOE_NETWORK.update(managedSanUri    = \'{}\')".format(managedSanUri))




        con_template = oneview_client.connection_templates.get(connectionTemplateUri)
        bandwidth    = con_template['bandwidth']
        tBandwidth   = bandwidth['typicalBandwidth']
        mBandwidth   = bandwidth['maximumBandwidth']



        scriptCode.append("# Create FCOE network {}".format(name)                                                                                       )
        scriptCode.append("net                      = oneview_client.fcoe_networks.create(FCOE_NETWORK)"                                                )
        scriptCode.append("con_template             = oneview_client.connection_templates.get(net[\'connectionTemplateUri\'])"                          )
        scriptCode.append("con_template[\'bandwidth\'][\'typicalBandwidth\']             = \'{}\')".format(tBandwidth)                                  )
        scriptCode.append("con_template[\'bandwidth\'][\'maximumBandwidth\']             = \'{}\')".format(mBandwidth)                                  )
        scriptCode.append("con_template_updated     = oneview_client.connection_templates.update(con_template)"                                         )

    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)

# ================================================================================================
#
#   generate_network_sets_script
#
# ================================================================================================
def generate_network_sets_script(to_file):
    scriptCode      = []
    network_sets       = oneview_client.network_sets.get_all_without_ethernet()
    for netset in network_sets:
        name                    = netset["name"]
        description             = netset["description"]
        nativeNetworkUri        = netset["nativeNetworkUri"]
        networkUris             = netset["networkUris"]
        connectionTemplateUri   = netset['connectionTemplateUri']



        #nativeNet_dest  = oneview_client.ethernet_networks.get_by('name', nativeNetName)

        scriptCode.append(CR)
        scriptCode.append("#===================Attributes for network set {} ========================".format(name)                                         )

        scriptCode.append("NETWORK_SET                                                  = dict()"                                                       )
        scriptCode.append("NETWORK_SET.update(name                                      = \'{}\')".format(name)                                         )
        if description is not None:
            scriptCode.append("NETWORK_SET.update(description                               = \'{}\')".format(description)                              )

        scriptCode.append("NETWORK_SET.update(networkUris                               = []"                                                           )
        for _net_uri in networkUris:
            net_uri             = build_uri(_net_uri)   #build_netUri('Ethernet',_net_uri) 
            scriptCode.append("NETWORK_SET[\'networkUris\'].append({})".format(net_uri)                                                                 )          


 
        con_template = oneview_client.connection_templates.get(connectionTemplateUri)
        bandwidth    = con_template['bandwidth']
        tBandwidth   = bandwidth['typicalBandwidth']
        mBandwidth   = bandwidth['maximumBandwidth']


        scriptCode.append("# Create network set {}".format(name)                                                                                        )
        scriptCode.append("net                      = oneview_client.network_sets.create(NETWORK_SET)"                                                  )
        scriptCode.append("con_template             = oneview_client.connection_templates.get(net[\'connectionTemplateUri\'])"                          )
        scriptCode.append("con_template[\'bandwidth\'][\'typicalBandwidth\']             = \'{}\')".format(tBandwidth)                                  )
        scriptCode.append("con_template[\'bandwidth\'][\'maximumBandwidth\']             = \'{}\')".format(mBandwidth)                                  )
        scriptCode.append("con_template_updated     = oneview_client.connection_templates.update(con_template)"                                         )


    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)


# ================================================================================================
#
#   generate_logical_interconnect_groups_script
#
# ================================================================================================
def generate_logical_interconnect_groups_script(to_file):
    scriptCode                  = []
    build_import_files(scriptCode)
    build_constants(scriptCode)
    build_config(scriptCode)
    

    logical_interconnect_groups = oneview_client.logical_interconnect_groups.get_all()
 
    for lig in logical_interconnect_groups:
        name                        = lig["name"]
        description                 = lig["description"] 
        enclosureType               = lig["enclosureType"]
        category                    = lig["category"]
        enclosureIndexes            = lig["enclosureIndexes"]                       # []
        interconnectBaySet          = lig["interconnectBaySet"]
        redundancyType              = lig["redundancyType"]

        internalNetworkUris         = lig["internalNetworkUris"]                    # []
        uplinkSets                  = lig["uplinkSets"]                             # []

        stackingMode                = lig["stackingMode"]

        # ethernetSettings
        ethernetSettings            = lig["ethernetSettings"]
        interconnectType            = ethernetSettings["interconnectType"]
        ethernetSettingsType        = ethernetSettings["type"]
        igmpSnooping                = ethernetSettings["enableIgmpSnooping"]
        igmpIdleTimeout             = ethernetSettings["igmpIdleTimeoutInterval"]
        networkLoopProtection       = ethernetSettings["enableNetworkLoopProtection"]
        pauseFloodProtection        = ethernetSettings["enablePauseFloodProtection"]
        enableRichTLV               = ethernetSettings["enableRichTLV"]
        taggedLldp                  = ethernetSettings["enableTaggedLldp"]
        lldpIpv6Address             = ethernetSettings["lldpIpv6Address"]
        lldpIpv4Address             = ethernetSettings["lldpIpv4Address"]
        fastMacCacheFailover        = ethernetSettings["enableFastMacCacheFailover"]
        macRefreshInterval          = ethernetSettings["macRefreshInterval"]


            #stormControl            = ethernetSettings["enableStormControl"]
            #stormControlThreshold   = ethernetSettings["stormControlThreshold"]
            #stormControlPolling     = ethernetSettings["stormControlPollingInterval"]


        # Interconnect Map Templates
        ICmapTemplate               = lig["interconnectMapTemplate"]
        ICmapEntryTemplates         = ICmapTemplate["interconnectMapEntryTemplates"]        #[]

        # telemetry
        telemetry                   = lig["telemetryConfiguration"]
        enableTelemetry             = telemetry["enableTelemetry"]
        sampleCount                 = telemetry["sampleCount"]
        sampleInterval              = telemetry["sampleInterval"]

        #qosConfiguration
        qosConfiguration            = lig["qosConfiguration"]
        qosDescription              = qosConfiguration["description"]
        inactiveFCoEQosConfig       = qosConfiguration["inactiveFCoEQosConfig"]
        inactiveNonFCoEQosConfig    = qosConfiguration["inactiveFCoEQosConfig"]
        activeQosConfig             = qosConfiguration["activeQosConfig"]
        activeQosName               = activeQosConfig["name"]
        activeQosDescription        = activeQosConfig["description"]
        activeQosconfigType         = activeQosConfig["configType"]
        downlinkClassificationType  = activeQosConfig["downlinkClassificationType"]
        uplinkClassificationType    = activeQosConfig["uplinkClassificationType"]
        qosTrafficClassifiers       = activeQosConfig["qosTrafficClassifiers"]          # []

        # snmp
        snmp                        = lig["snmpConfiguration"]
        snmpName                    = snmp["name"]
        snmpDescription             = snmp["description"]
        snmpreadCommunity           = snmp["readCommunity"]
        snmpDescription             = snmp["description"]
        snmpEnabled                 = snmp["enabled"]
        snmpSystemContact           = snmp["systemContact"]
        snmpEnabled                 = snmp["enabled"]
        snmpAccess                  = snmp["snmpAccess"]            # []
        snmptrapDestinations        = snmp["trapDestinations"]      # []

        scriptCode.append(CR)
        scriptCode.append("#===================Attributes for Logical Interconnect Group {} ========================".format(name)                      )

        scriptCode.append("LOGICAL_INTERCONNECT_GROUP                                   = dict()"                                                       )
        scriptCode.append("LOGICAL_INTERCONNECT_GROUP.update(name                       = \'{}\')".format(name)                                         )
        if description is not None:
            scriptCode.append("LOGICAL_INTERCONNECT_GROUP.update(description                = \'{}\')".format(description)                              )
        scriptCode.append("LOGICAL_INTERCONNECT_GROUP.update(enclosureType              = \'{}\')".format(enclosureType)                                )
        scriptCode.append("LOGICAL_INTERCONNECT_GROUP.update(redundancyType             = \'{}\')".format(redundancyType)                               )
        scriptCode.append("LOGICAL_INTERCONNECT_GROUP.update(interconnectBaySet         = {})".format(interconnectBaySet)                               ) 

        # ethernetSettings
        if -1 not in enclosureIndexes:                          # Check if not VC-FC
            scriptCode.append(CR + "##### ethernetSettings region"                                                                                      )
            scriptCode.append("LOGICAL_INTERCONNECT_GROUP.update(ethernetSettings           = dict() )"                                                 )
            scriptCode.append("ethernetSettings                                             = LOGICAL_INTERCONNECT_GROUP[\'ethernetSettings\']"         )
            scriptCode.append("ethernetSettings.update(type                                 = \'{}\')".format(ethernetSettingsType)                     )
            scriptCode.append("ethernetSettings.update(enableIgmpSnooping                   = \'{}\')".format(igmpSnooping)                             )
            scriptCode.append("ethernetSettings.update(igmpIdleTimeoutInterval              = \'{}\')".format(igmpIdleTimeout)                          )
            scriptCode.append("ethernetSettings.update(enableNetworkLoopProtection          = \'{}\')".format(networkLoopProtection)                    )
            scriptCode.append("ethernetSettings.update(enablePauseFloodProtection           = \'{}\')".format(pauseFloodProtection)                     )
            scriptCode.append("ethernetSettings.update(enableRichTLV                        = \'{}\')".format(enableRichTLV)                            )
            scriptCode.append("ethernetSettings.update(enableTaggedLldp                     = \'{}\')".format(taggedLldp)                               )
            scriptCode.append("ethernetSettings.update(enableFastMacCacheFailover           = \'{}\')".format(fastMacCacheFailover)                     )
            scriptCode.append("ethernetSettings.update(macRefreshInterval                   = \'{}\')".format(macRefreshInterval)                       )
            scriptCode.append("ethernetSettings.update(lldpIpv4Address                      = \'{}\')".format(lldpIpv4Address)                          )
            scriptCode.append("ethernetSettings.update(lldpIpv6Address                      = \'{}\')".format(lldpIpv6Address)                          )


        # Enclosure Indexes

        scriptCode.append(CR + "##### enclosure Indexes region"                                                                                         )
        scriptCode.append("indexArray                                                  = []"                                                            )
        for index in enclosureIndexes:
            scriptCode.append("indexArray.append({})".format(index) )
        
        scriptCode.append("LOGICAL_INTERCONNECT_GROUP.update(enclosureIndexes          = [])"                                                           )
        scriptCode.append("for index in indexArray:"                                                                                                    )
        scriptCode.append("     LOGICAL_INTERCONNECT_GROUP[\'enclosureIndexes\'].append(index)"                                                         )


        # InterConnect Map Templates
        scriptCode.append(CR + "##### InterConnect Map Templates region"                                                                                )
        scriptCode.append("LOGICAL_INTERCONNECT_GROUP.update(interconnectMapTemplate   = dict())"                                                       )
        scriptCode.append("LOGICAL_INTERCONNECT_GROUP[\'interconnectMapTemplate\'].update(interconnectMapEntryTemplates = [])"                          )
        scriptCode.append("interconnectMapEntryTemplates = LOGICAL_INTERCONNECT_GROUP[\'interconnectMapTemplate\'][\'interconnectMapEntryTemplates\']"  )
                                                                
        for mapEntryTemplate in ICmapEntryTemplates:
            logicalLocation         = mapEntryTemplate["logicalLocation"]
            scriptCode.append("map_entry_template                                           = dict()"                                                   )           
            scriptCode.append("map_entry_template.update(logicalLocation                    = dict())"                                                  )  
            scriptCode.append("logicalLocation                                              = map_entry_template[\'logicalLocation\']"                  )    
            scriptCode.append("location_entries                                             = []"                                                       )     
            for entry in logicalLocation["locationEntries"]:
                relativeValue       = entry["relativeValue"]
                _type               = entry["type"]
                if "Enclosure" == _type:
                    enclosureIndex  = relativeValue
                scriptCode.append(CR                                                                                                                    )
                scriptCode.append("location_entry                                               = dict()"                                               )
                scriptCode.append("location_entry.update(relativeValue                          = {})".format(relativeValue)                            )
                scriptCode.append("location_entry.update(type                                   = \'{}\')".format(_type)                                )
                scriptCode.append("location_entries.append(location_entry)"                                                                             )
                scriptCode.append("logicalLocation.update(locationEntries                       = location_entries)"                                    )

            scriptCode.append("map_entry_template.update(enclosureIndex                     = {})".format(enclosureIndex)                               ) 
            
            icTypeUri                   =  mapEntryTemplate["permittedInterconnectTypeUri"] 
            if icTypeUri is not None:
                icName                  = oneview_client.interconnect_types.get(icTypeUri)["name"]
                scriptCode.append("icTypeUri                                                    = oneview_client.interconnect_types.get_by(\'name\',\'{}\')[0][\'uri\']".format(icName)  )
                scriptCode.append("map_entry_template.update(permittedInterconnectTypeUri       = icTypeUri)"                                           )

            scriptCode.append("interconnectMapEntryTemplates.append(map_entry_template)"                                                                )

        # uplinksets
        scriptCode.append(CR + "##### Uplink Sets region"                                                                                               )
        scriptCode.append("LOGICAL_INTERCONNECT_GROUP.update(uplinkSets                 = [])"                                                          )  
        
        for upl in uplinkSets:
            uplName                 = upl["name"]
            nativeNetworkUri        = upl["nativeNetworkUri"]
            networkUris             = upl["networkUris"]                # []
            networkType             = upl["networkType"]
            ethernetNetworkType     = upl["ethernetNetworkType"]
            lacpTimer               = upl["lacpTimer"]
            mode                    = upl["mode"]
            upl_logicalPortConfigs  = upl["logicalPortConfigInfos"]     #[]

    
    
            scriptCode.append("upl_element                                                  = dict()"                                                   )
            scriptCode.append("upl_element.update(name                                      = \'{}\')".format(uplName)                                  )
            scriptCode.append("upl_element.update(networkType                               = \'{}\')".format(networkType)                              )
            scriptCode.append("upl_element.update(mode                                      = \'{}\')".format(mode)                                     )
            if 'Ethernet' == networkType:
                scriptCode.append("upl_element.update(ethernetNetworkType                       = \'{}\')".format(ethernetNetworkType)                  )
                scriptCode.append("upl_element.update(lacpTimer                                 = \'{}\')".format(lacpTimer)                            )
            
            if nativeNetworkUri is not None:
                net_uri = build_netUri(networkType,nativeNetworkUri)  
                scriptCode.append("upl_element.update(nativeNetworkUri                          = {})".format(net_uri)                                  )
            
            scriptCode.append("upl_element.update(networkUris = [])"                                                                                    )
            for _net_uri in networkUris:
                net_uri             = build_netUri(networkType,_net_uri) 
                scriptCode.append("upl_element[\'networkUris\'].append({})".format(net_uri)                                                             )
    

            scriptCode.append("upl_element.update(logicalPortConfigInfos = [])"                                                                         )
            scriptCode.append("lpci_array                                                   = upl_element[\'logicalPortConfigInfos\']"                  )
            for upl_logical_port_config in upl_logicalPortConfigs:
                scriptCode.append("lpci_element                                                 = dict()"                                               )
                scriptCode.append("lpci_element.update(desiredSpeed                             = \'{}\')".format(upl_logical_port_config['desiredSpeed'])  )
                scriptCode.append("lpci_element.update(logicalLocation                          = dict())"                                              )
                scriptCode.append("lpci_element[\'logicalLocation\'].update(locationEntries   = [])"                                                    )
                upl_logicalLocation     = upl_logical_port_config['logicalLocation']

                for upl_entry in upl_logicalLocation["locationEntries"]:
                    upl_relativeValue       = upl_entry["relativeValue"]
                    upl_type                = upl_entry["type"]
                    scriptCode.append(CR                                                                                                                 )
                    scriptCode.append("location_entry                                               = dict()"                                            )
                    scriptCode.append("location_entry.update(relativeValue                          = {})".format(upl_relativeValue)                     )
                    scriptCode.append("location_entry.update(type                                   = \'{}\')".format(upl_type)                          )
                    scriptCode.append("lpci_element[\'logicalLocation\'][\'locationEntries\'].append(location_entry)"                                    )

                scriptCode.append("lpci_array.append(lpci_element)"                                                                                      )
            
            # Add entry to  the uplinkSets array
            scriptCode.append("LOGICAL_INTERCONNECT_GROUP[\'uplinkSets\'].append(upl_element)"                                                           )
            
        scriptCode.append(CR + "##### QOS - TBD"                                                                                                         )
        scriptCode.append(CR + "##### SNMP - TBD"                                                                                                        )
        
        
        
        scriptCode.append("")
        scriptCode.append("#  Creating logical interconnect group ")
        scriptCode.append("lig      = oneview_client.logical_interconnect_groups.create(LOGICAL_INTERCONNECT_GROUP)")

    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)


# ================================================================================================
#
#   generate_sas_logical_interconnect_groups_script
#
# ================================================================================================
def generate_sas_logical_interconnect_groups_script(to_file):
    
    scriptCode                  = []
    build_import_files(scriptCode)
    build_constants(scriptCode)
    build_config(scriptCode)
    
    
    logical_interconnect_groups = oneview_client.sas_logical_interconnect_groups.get_all()
 
    for lig in logical_interconnect_groups:
        name                        = lig["name"]
        description                 = lig["description"] 
        enclosureType               = lig["enclosureType"]
        category                    = lig["category"]                    
        interconnectBaySet          = lig["interconnectBaySet"]
        enclosureIndexes            = lig["enclosureIndexes"] 


        # Interconnect Map Templates
        ICmapTemplate               = lig["interconnectMapTemplate"]
        ICmapEntryTemplates         = ICmapTemplate["interconnectMapEntryTemplates"]        #[]
      


        scriptCode.append(CR)
        scriptCode.append("#===================Attributes for Logical Interconnect Group {} ========================".format(name)                      )

        scriptCode.append("LOGICAL_INTERCONNECT_GROUP                                   = dict()"                                                       )
        scriptCode.append("LOGICAL_INTERCONNECT_GROUP.update(name                       = \'{}\')".format(name)                                         )
        if description is not None:
            scriptCode.append("LOGICAL_INTERCONNECT_GROUP.update(description                = \'{}\')".format(description)                              )  
        scriptCode.append("LOGICAL_INTERCONNECT_GROUP.update(enclosureType              = \'{}\')".format(enclosureType)                                )                              
        scriptCode.append("LOGICAL_INTERCONNECT_GROUP.update(interconnectBaySet         = {})".format(interconnectBaySet)                               )

        
        scriptCode.append(CR + "##### enclosure Indexes region"                                                                                         )
        scriptCode.append("indexArray                                                  = []"                                                            )
        for index in enclosureIndexes:
            scriptCode.append("indexArray.append({})".format(index)                                                                                     )
        
        scriptCode.append("LOGICAL_INTERCONNECT_GROUP.update(enclosureIndexes          = [])"                                                           )
        scriptCode.append("for index in indexArray:"                                                                                                    )
        scriptCode.append("     LOGICAL_INTERCONNECT_GROUP[\'enclosureIndexes\'].append(index)"                                                         )   


        scriptCode.append(CR + "##### InterConnect Map Templates region"                                                                                )
        scriptCode.append("LOGICAL_INTERCONNECT_GROUP.update(interconnectMapTemplate   = dict())"                                                       )
        scriptCode.append("LOGICAL_INTERCONNECT_GROUP[\'interconnectMapTemplate\'].update(interconnectMapEntryTemplates = [])"                          )
        scriptCode.append("interconnectMapEntryTemplates = LOGICAL_INTERCONNECT_GROUP[\'interconnectMapTemplate\'][\'interconnectMapEntryTemplates\']"  )
                                                                
        for mapEntryTemplate in ICmapEntryTemplates:
            logicalLocation         = mapEntryTemplate["logicalLocation"]
            scriptCode.append("map_entry_template                                           = dict()"                                                   )           
            scriptCode.append("map_entry_template.update(logicalLocation                    = dict())"                                                  )  
            scriptCode.append("logicalLocation                                              = map_entry_template[\'logicalLocation\']"                  )    
            scriptCode.append("location_entries                                             = []"                                                       )     
            for entry in logicalLocation["locationEntries"]:
                relativeValue       = entry["relativeValue"]
                _type               = entry["type"]
                if "Enclosure" == _type:
                    enclosureIndex  = relativeValue
                scriptCode.append(CR                                                                                                                    )
                scriptCode.append("location_entry                                               = dict()"                                               )
                scriptCode.append("location_entry.update(relativeValue                          = {})".format(relativeValue)                            )
                scriptCode.append("location_entry.update(type                                   = \'{}\')".format(_type)                                )
                scriptCode.append("location_entries.append(location_entry)"                                                                             )
                scriptCode.append("logicalLocation.update(locationEntries                       = location_entries)"                                    )

            scriptCode.append("map_entry_template.update(enclosureIndex                     = {})".format(enclosureIndex)                               ) 
            
            icTypeUri                   =  mapEntryTemplate["permittedInterconnectTypeUri"] 
            if icTypeUri is not None:
                icName                  = oneview_client.sas_interconnect_types.get(icTypeUri)["name"]
                scriptCode.append("icTypeUri                                                    = oneview_client.sas_interconnect_types.get_by(\'name\',\'{}\')[0][\'uri\']".format(icName)  )
                scriptCode.append("map_entry_template.update(permittedInterconnectTypeUri       = icTypeUri)"                                           )

            scriptCode.append("interconnectMapEntryTemplates.append(map_entry_template)"                                                                )


        
        scriptCode.append("")
        scriptCode.append("#  Creating SAS logical interconnect group ")
        scriptCode.append("lig      = oneview_client.sas_logical_interconnect_groups.create(SAS_LOGICAL_INTERCONNECT_GROUP)")

    
    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)



# ================================================================================================
#
#   generate_enclosure_groups_script
#
# ================================================================================================
def generate_enclosure_groups_script(to_file):

    scriptCode                  = []
    build_import_files(scriptCode)
    build_constants(scriptCode)
    build_config(scriptCode)
    
    enclosure_groups = oneview_client.enclosure_groups.get_all()
    #enclosure_groups = oneview_client.enclosure_groups.get_all(sort='name:descending')
    for eg in enclosure_groups:
        name                                = eg["name"]
        description                         = eg["description"]  
        ipAddressingMode                    = eg["ipAddressingMode"]
        ipRangeUris                         = eg["ipRangeUris"]                         #[]
        enclosureCount                      = eg["enclosureCount"]
        powerMode                           = eg["powerMode"]
        stackingMode                        = eg["stackingMode"]
        ambientTemperatureMode              = eg["ambientTemperatureMode"]
        associatedLogicalInterconnectGroups = eg["associatedLogicalInterconnectGroups"] #[]
        interconnectBayMappings             = eg["interconnectBayMappings"]             #[]
        osDeploymentSettings                = eg["osDeploymentSettings"]                # dict



        scriptCode.append(CR)
        scriptCode.append("#===================Attributes for Enclosure Group {} ========================".format(name)                                 )

        scriptCode.append("ENCLOSURE_GROUP                                              = dict()"                                                       )
        scriptCode.append("ENCLOSURE_GROUP.update(name                                  = \'{}\')".format(name)                                         )
        if description is not None:
            scriptCode.append("ENCLOSURE_GROUP.update(description                           = \'{}\')".format(description)                              )  
        scriptCode.append("ENCLOSURE_GROUP.update(enclosureCount                        = {})".format(enclosureCount)                                   )
        scriptCode.append("ENCLOSURE_GROUP.update(powerMode                             = \'{}\')".format(powerMode)                                    )
        scriptCode.append("ENCLOSURE_GROUP.update(stackingMode                          = \'{}\')".format(stackingMode)                                 )
        scriptCode.append("ENCLOSURE_GROUP.update(ambientTemperatureMode                = \'{}\')".format(ambientTemperatureMode)                       )

        ## IP ranges
        scriptCode.append(CR)
        scriptCode.append("### IP Ranges region"                                                                                                        ) 
        scriptCode.append("ENCLOSURE_GROUP.update(ipAddressingMode                      = \'{}\')".format(ipAddressingMode)                             )
        if ipRangeUris is not None:
            scriptCode.append("ENCLOSURE_GROUP.update(ipRangeUris                           = [])"                                                      )
            for ip_range_uri in ipRangeUris:
                scriptCode.append("res                                                          = oneview_client.id_pools_ipv4_ranges.get(\'{}\')".format(ip_range_uri) )
                scriptCode.append("res_name                                                     = res[\'name\']"                                        )
                scriptCode.append("pool_type_ipv4                                               = \'ipv4\'"                                             )
                scriptCode.append("ipv4_pools                                                   = oneview_client.id_pools.get(pool_type_ipv4)"          )
                scriptCode.append("for range_uri in ipv4_pools[\'rangeUris\']:"                                                                         )
                scriptCode.append("     this_pool = oneview_client.id_pools_ipv4_ranges.get(range_uri)"                                                 )
                scriptCode.append("     if res_name == this_pool[\'name\']:"                                                                            )
                scriptCode.append("         res_uri = this_pool[\'uri\'] "                                                                              )
                scriptCode.append("         ENCLOSURE_GROUP[\'ipRangeUris\'].append(res_uri)"                                                           )      

        ## Associated Logical Interconnect Groups
        scriptCode.append(CR)
        scriptCode.append("### associatedLogicalInterconnectGroups region"                                                                              ) 
        scriptCode.append("ENCLOSURE_GROUP.update(associatedLogicalInterconnectGroups   = [])"                                                          )
        for lig_uri in associatedLogicalInterconnectGroups:
            res_uri             = build_uri(lig_uri)
            scriptCode.append("res_uri                                                      = {}".format(build_uri(lig_uri))                            )
            scriptCode.append("ENCLOSURE_GROUP[\'associatedLogicalInterconnectGroups\'].append(res_uri)"                                                )

        ## Interconnect Bay mappings
        scriptCode.append(CR)
        scriptCode.append("### Interconnect Bay mappings region"                                                                                        ) 
        scriptCode.append("ENCLOSURE_GROUP.update(interconnectBayMappings               = [])"                                                          )
        for ic_bay_mapping in interconnectBayMappings:
            lig_uri             = ic_bay_mapping['logicalInterconnectGroupUri']
            res_uri             = build_uri(lig_uri)
            ic_bay              = ic_bay_mapping['interconnectBay']

            scriptCode.append(""                                                                                                                        )
            scriptCode.append("bay_mapping                                                  = dict()"                                                   )
            scriptCode.append("res_uri                                                      = {}".format(build_uri(lig_uri))                            )
            scriptCode.append("bay_mapping.update(logicalInterconnectGroupUri               = res_uri )"                                                )
            scriptCode.append("bay_mapping.update(interconnectBay                           = {})".format(ic_bay)                                       )
            if 'enclosureIndex' in ic_bay_mapping: 
                enc_index       = ic_bay_mapping['enclosureIndex']
                scriptCode.append("bay_mapping.update(enclosureIndex                        = {})".format(enc_index)                                    )
        
            scriptCode.append("ENCLOSURE_GROUP[\'interconnectBayMappings\'].append(bay_mapping)"                                                        )       
    
        ## OS Deployment Settings
        scriptCode.append(CR)
        scriptCode.append("### OS Deployment Settings region"                                                                                           ) 
        scriptCode.append("ENCLOSURE_GROUP.update(osDeploymentSettings                      = dict())"                                                  )
        scriptCode.append("ENCLOSURE_GROUP[\'osDeploymentSettings\'].update(deploymentModeSettings  = dict())"                                          )
        deployment_mode        = osDeploymentSettings['deploymentModeSettings']['deploymentMode']
        scriptCode.append("ENCLOSURE_GROUP[\'osDeploymentSettings\'][\'deploymentModeSettings\'].update(deploymentMode  = \'{}\')".format(deployment_mode))
        deployment_net_uri     = osDeploymentSettings['deploymentModeSettings']['deploymentNetworkUri']
        if deployment_net_uri:
            scriptCode.append("res_uri                                                      = {}".format(build_uri(deployment_net_uri))                 )
            scriptCode.append("ENCLOSURE_GROUP[\'osDeploymentSettings\'][\'deploymentModeSettings\'].update(deploymentNetworkUri  = res_uri)"           )


        scriptCode.append("ENCLOSURE_GROUP[\'osDeploymentSettings\'].update(manageOSDeployment = {})".format(osDeploymentSettings['manageOSDeployment'])) 
                                            
        scriptCode.append("print(json.dumps(ENCLOSURE_GROUP, indent=4))"                                                                                )
        scriptCode.append(CR)
        scriptCode.append("#  Creating EnclosureGroup group "                                                                                           )
        scriptCode.append("eg      = oneview_client.enclosure_groups.create(ENCLOSURE_GROUP)"                                                           )



    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)


# ================================================================================================
#
#   generate_profile_or_template_script - helper function
#
# ================================================================================================
def generate_profile_or_templates_script(scriptCode, prof):

    category                            = prof["category"]
    isTemplate                          = 'server-profile-templates' in category
    name                                = prof["name"]
    description                         = prof["description"]  
    affinity                            = prof["affinity"]
    serverHardwareTypeUri               = prof["serverHardwareTypeUri"]                         
    enclosureGroupUri                   = prof["enclosureGroupUri"]
    wwnType                             = prof["wwnType"]
    macType                             = prof["macType"]
    serialNumberType                    = prof["serialNumberType"]
    iscsiInitiatorNameType              = prof["iscsiInitiatorNameType"]
    hideUnusedFlexNics                  = prof["hideUnusedFlexNics"]

    bios                                = prof["bios"]                               # dict
    boot                                = prof["boot"]                               # dict      
    bootMode                            = prof["bootMode"]                           # dict   
    firmware                            = prof["firmware"]                           # dict
    localStorage                        = prof["localStorage"]                       # dict
    sanStorage                          = prof["sanStorage"]                         # dict
    osDeploymentSettings                = prof["osDeploymentSettings"]               # dict
    if isTemplate:
        connectionSettings                  = prof["connectionSettings"]                 # dict
    else:
        connectionSettings                  = prof["connections"]                 # dict


    #print("#===================Attributes for {0} {1} ========================".format(category,name)                   )

    ###
    scriptCode.append("PROFILE.update(affinity                      = \'{}\')".format(affinity)                                                         )
    scriptCode.append("PROFILE.update(wwnType                       = \'{}\')".format(wwnType)                                                          )
    scriptCode.append("PROFILE.update(macType                       = \'{}\')".format(macType)                                                          )
    scriptCode.append("PROFILE.update(serialNumberType              = \'{}\')".format(serialNumberType)                                                 )
    scriptCode.append("PROFILE.update(iscsiInitiatorNameType        = \'{}\')".format(iscsiInitiatorNameType)                                           )
    scriptCode.append("PROFILE.update(hideUnusedFlexNics            = {})".format(hideUnusedFlexNics)                                                   )
    if serverHardwareTypeUri is not None:
        scriptCode.append("sht                                          = oneview_client.server_hardware_types.get(\'{}\')".format(serverHardwareTypeUri) )
        scriptCode.append("res_name                                     = sht[\'name\']"                                                                )
        scriptCode.append("all_sht                                      = oneview_client.server_hardware_types.get_all()"                               )
        scriptCode.append("for sht in all_sht: "                                                                                                        )
        scriptCode.append("     if res_name == sht[\'name\']:"                                                                                          )
        scriptCode.append("         PROFILE.update(serverHardwareTypeUri = sht[\'uri\'])"                                                               )

    if enclosureGroupUri is not None:
        scriptCode.append("eg_uri                                       = {}".format(build_uri(enclosureGroupUri))                                      )
        scriptCode.append("PROFILE.update(enclosureGroupUri             = eg_uri)"                                                                      )


    # Boot and bootMode
    scriptCode.append("PROFILE.update(boot                          = dict() )"                                                                         )
    scriptCode.append("PROFILE[\'boot\'].update(manageBoot            = {})".format(boot['manageBoot'])                                                 )
    scriptCode.append("PROFILE[\'boot\'].update(order                 = [])"                                                                            )
    for boot_entry in boot['order']:
        scriptCode.append("PROFILE[\'boot\'][\'order\'].append(\'{}\')".format(boot_entry)                                                              )

    scriptCode.append("PROFILE.update(bootMode                      = dict() )"                                                                         )
    scriptCode.append("PROFILE[\'bootMode\'].update(manageMode        = {})".format(bootMode['manageMode'])                                             )
    scriptCode.append("PROFILE[\'bootMode\'].update(pxeBootPolicy     = \'{}\')".format(bootMode['pxeBootPolicy'])                                      )
    scriptCode.append("PROFILE[\'bootMode\'].update(mode              = \'{}\')".format(bootMode['mode'])                                               )


    # Connection Settings region
    scriptCode.append(CR)
    scriptCode.append("##### Connection Settings region               "                                                                                 )
    # Difference between SP and SPT here
    if isTemplate:
        scriptCode.append("PROFILE.update(connectionSettings            = dict() )"                                                                     )
        scriptCode.append("PROFILE[\'connectionSettings\'].update(manageConnections = {})".format(connectionSettings['manageConnections'])              )
        scriptCode.append("PROFILE[\'connectionSettings\'].update(connections = [])"                                                                    )
        connections             =  connectionSettings['connections']  
        scriptCode.append("connections                                  = PROFILE[\'connectionSettings\']['connections\']"                              )                                                
    else:
       scriptCode.append("PROFILE.update(connections = [])"                                                                                             ) 
       connections              =  connectionSettings 
       scriptCode.append("connections                                  = PROFILE['connections\']"                                                       )
    
    if connections:
        for con_element in connections:
            functionType        = con_element['functionType']
            priority            = con_element['boot']['priority']
            con_name            = con_element['name']

            scriptCode.append("#--------------------- Attributes for connection \'{}\'".format(con_name)                                                )
            scriptCode.append("connection_element                           = dict() "                                                                  )
            scriptCode.append("connection_element.update(name               = \'{}\')".format(con_name)                                                 )
            scriptCode.append("net_uri                                      = {}".format(build_uri(con_element['networkUri'] ) )                        )
            scriptCode.append("connection_element.update(networkUri         = net_uri)"                                                                 )                
            scriptCode.append("connection_element.update(portId             = \'{}\')".format(con_element['portId']     )                               )
            scriptCode.append("connection_element.update(requestedMbps      = \'{}\')".format(con_element['requestedMbps'] )                            )
            scriptCode.append("connection_element.update(requestedVFs       = \'{}\')".format(con_element['requestedVFs'] )                             )
            scriptCode.append("connection_element.update(functionType       = \'{}\')".format(functionType )                                            )
            
            ## boot dict
            scriptCode.append("connection_element.update(boot               = dict() )"                                                                 )
            scriptCode.append("connection_element[\'boot\'].update(priority   = \'{}\')".format(priority)                                               )
            
            # Difference between SP and SPT here
            if isTemplate:
                if con_element['boot']['bootVlanId']:
                    scriptCode.append("connection_element[\'boot\'].update(bootVlanId = \'{}\')".format(con_element['boot']['bootVlanId'])              )
            

            # define custom boot type
            if 'NotBootable' not in priority:                                               # Could be PXE , iscsci or SAN
                if 'Ethernet' in functionType:
                    scriptCode.append("connection_element[\'boot\'].update(ethernetBootType = \'{}\')".format(con_element['boot']['ethernetBootType'])  )   # PXE  
                    # need to work iSCSI boot
                if 'FibreChannel' in functionType:
                    bootVolumeSource    = con_element['boot']['bootVolumeSource']
                    scriptCode.append("connection_element[\'boot\'].update(bootVolumeSource = \'{}\')".format(bootVolumeSource)                         )   # Managed Volume
                    #if not isTemplate:  # applies to Server profile only
                    #    if 'ManagedVolume' in bootVolumeSource:
                    #        scriptCode.append("connection_element[\'boot\'].update(targets               = [] )"                            )
                    #        targets         = con_element['boot']['targets']
                    #        for target_element in targets:      # TO BE reviewed as lun and Wwpn depends on the SANstorage section
                    #            scriptCode.append("target                                       = dict()"                                   )
                    #            scriptCode.append("target.update(lun                            = {})".format(target_element['lun'])        )
                    #            scriptCode.append("target.update(arrayWwpn                      = {})".format(target_element['arrayWwpn'])  )
                    #        scriptCode.append("connection_element['boot']['targets'].append(target)"                                        )                       

            scriptCode.append("connections].append(connection_element)"                                                                                 )


    
    # local Storage region
    scriptCode.append(CR)
    scriptCode.append("##### local Storage region               "                                                                                       )
    scriptCode.append("PROFILE.update(localStorage                  = dict() )"                                                                         )
    ## Controllers section
    scriptCode.append("#####    local Storage - Controllers            "                                                                                )
    scriptCode.append("PROFILE[\'localStorage\'].update(controllers   = [] )"                                                                           )
    for controller in localStorage['controllers']:
        scriptCode.append("controller                                   = dict()"                                                                       )
        scriptCode.append("controller.update(deviceSlot                 = \'{}\')".format(controller['deviceSlot'])                                     )
        scriptCode.append("controller.update(initialize                 = {})".format(controller['initialize'] )                                        )
        scriptCode.append("controller.update(mode                       = \'{}\')".format(controller['mode'] )                                          )
        # logical Drives
        if controller['logicalDrives'] is not None:
            scriptCode.append("controller.update(logicalDrives                  = [] )"                                                                 )
            for ld in controller['logicalDrives']:
                scriptCode.append("ld                                           = dict()"                                                               )
                if ld['name'] is not None:
                    scriptCode.append("ld.update(name                               = \'{}\')".format(ld['name'])                                       ) 
                scriptCode.append("ld.update(bootable                           = {})".format(ld['bootable']) 	                                        )
                scriptCode.append("ld.update(raidLevel                          = \'{}\')".format(ld['raidLevel']) 	                                    ) 
                scriptCode.append("ld.update(sasLogicalJBODId                   = {})".format(ld['sasLogicalJBODId'])                                   )                    
                if ld['driveTechnology'] is not None:
                    scriptCode.append("ld.update(driveTechnology                    = \'{}\')".format(ld['driveTechnology'])                            )
                if ld['numPhysicalDrives'] is not None:
                    scriptCode.append("ld.update(numPhysicalDrives                  = {})".format(ld['numPhysicalDrives'])                              )
                scriptCode.append("controller[\'logicalDrives\'].append(ld) "                                                                           )
        scriptCode.append("PROFILE[\'localStorage\'][\'controllers\'].append(controller)"                                                               )

    ## sas Logical JBODs section
    scriptCode.append("#####    local Storage -  sas Logical JBODs            "                                                                         )
    scriptCode.append("PROFILE[\'localStorage\'].update(sasLogicalJBODs = [] )"                                                                         )
    for jbod in localStorage['sasLogicalJBODs']:
        scriptCode.append("jbod                                         = dict()"                                                                       )
        scriptCode.append("jbod.update(name                             = \'{}\')".format(jbod['name'])                                                 )
        scriptCode.append("jbod.update(deviceSlot                       = \'{}\')".format(jbod['deviceSlot'])                                           )
        scriptCode.append("jbod.update(driveTechnology                  = \'{}\')".format(jbod['driveTechnology'])                                      )

        scriptCode.append("jbod.update(driveMinSizeGB                   = {})".format(jbod['driveMinSizeGB'])                                           )
        scriptCode.append("jbod.update(driveMaxSizeGB                   = {})".format(jbod['driveMaxSizeGB'])                                           )
        scriptCode.append("jbod.update(numPhysicalDrives                = {})".format(jbod['numPhysicalDrives'])                                        )
        scriptCode.append("jbod.update(id                               = {})".format(jbod['id'])                                                       )
        scriptCode.append("PROFILE[\'localStorage\'][\'sasLogicalJBODs\'].append(jbod)"                                                                 )


    # Firmware
    scriptCode.append(CR)
    scriptCode.append("##### Firmware region               "                                                                                            )
    scriptCode.append("PROFILE.update(firmware                      = dict() )"                                                                         )
    scriptCode.append("PROFILE[\'firmware\'].update(manageFirmware    = {})".format(firmware['manageFirmware'])                                         )
    scriptCode.append("PROFILE[\'firmware\'].update(forceInstallFirmware = {})".format(firmware['forceInstallFirmware'])                                )
    if firmware['manageFirmware']:
        scriptCode.append("PROFILE[\'firmware\'].update(firmwareInstallType = \'{}\')".format(firmware['firmwareInstallType'] )                         )
        scriptCode.append("PROFILE[\'firmware\'].update(firmwareActivationType = \'{}\')".format(firmware['firmwareActivationType'])                    )
        scriptCode.append("PROFILE[\'firmware\'].update(firmwareBaselineUri = \'{}\')".format(firmware['firmwareBaselineUri'])                          )   


    # BIOS 
    manageBios                            = bios['manageBios']
    scriptCode.append(CR)
    scriptCode.append("##### BIOS settings region               "                                                                                       )
    scriptCode.append("PROFILE.update(bios                          = dict() )"                                                                         )
    scriptCode.append("PROFILE[\'bios\'].update(manageBios            = {}) ".format(manageBios)                                                        )
    scriptCode.append("PROFILE[\'bios\'].update(overriddenSettings    = []) "                                                                           )
    if manageBios:
        for setting in bios['overriddenSettings']:
            scriptCode.append("setting                                      = dict() "                                                                  )   
            scriptCode.append("setting.update(id                            = \'{}\')".format(setting['id'])                                            ) 
            scriptCode.append("setting.update(value                         = \'{}\')".format(setting['value'])                                         ) 
            scriptCode.append("PROFILE[\'bios\'][\'overriddenSettings\'].append(setting)"                                                               ) 

    # OS Deployment Settings
    scriptCode.append(CR)
    scriptCode.append("##### OS Deployment settings region               "                                                                              )
    scriptCode.append("PROFILE.update(osDeploymentSettings          = dict() )"                                                                         )
    if osDeploymentSettings:
        scriptCode.append("try:"                                                                                                                        )
        scriptCode.append("    deployment_plan_uri = \'{}\'".format(osDeploymentSettings['osDeploymentPlanUri'])                                        )
        scriptCode.append("    res_uri = oneview_client.os_deployment_plans.get(deployment_plan_uri)"                                                   )
        scriptCode.append("except HPOneViewException as error:"                                                                                         )
        scriptCode.append("    res_uri = \'\'   # OS Deployment plan not found"                                                                         )
        scriptCode.append("if res_uri:"                                                                                                                 )
        scriptCode.append("     PROFILE[\'osDeploymentSettings\'].update(osDeploymentPlanUri = \'res_uri\')"                                            )
        scriptCode.append("     PROFILE[\'osDeploymentSettings\'].update(osCustomAttributes = [] )"                                                     )
        for setting in osDeploymentSettings['osCustomAttributes']:
            scriptCode.append("     setting                                      = dict() "                                                             )   
            scriptCode.append("     setting.update(name                          = \'{}\')".format(setting['name'])                                     ) 
            scriptCode.append("     setting.update(value                         = \'{}\')".format(setting['value'])                                    ) 

            scriptCode.append("     PROFILE[\'osDeploymentSettings\'][\'osCustomAttributes\'].append(setting)"                                          ) 

    # San Storage region
    manageSanStorage        = sanStorage['manageSanStorage']
    scriptCode.append(CR)
    scriptCode.append("##### San Storage region               "                                                                                         )
    scriptCode.append("PROFILE.update(SanStorage                    = dict() )"                                                                         )
    scriptCode.append("PROFILE[\'sanStorage\'].update(volumeAttachments = [] )"                                                                         )
    scriptCode.append("PROFILE[\'sanStorage\'].update(manageSanStorage  = \'{}\' )".format(manageSanStorage)                                            )

    if manageSanStorage:
        scriptCode.append("PROFILE[\'sanStorage\'].update(hostOSType      = \'{}\')".format(sanStorage['hostOSType'])                                   )
        scriptCode.append("PROFILE[\'sanStorage\'][\'volumeAttachments\'] = dict() )"                                                                   )
        scriptCode.append("volumeAttachments                            = PROFILE[\'sanStorage\'][\'volumeAttachments\']  )"                            )

        volumeAttachments           = sanStorage['volumeAttachments']
        for volume in volumeAttachments:
            lunType                 = volume['lunType']         
            scriptCode.append("volume                                       = dict()"                                                                   )
            scriptCode.append("volume.update(lunType                        = \'{}\')".format(lunType)                                                  )
            scriptCode.append("volume.update(isBootVolume                   = {}    )".format(volume['isBootVolume'])                                   )    
            scriptCode.append("volume.update(id                             = {}    )".format(volume['id'])                                             )
            scriptCode.append("volume.update(lun                            = {}    )".format(volume['lun'])                                            )

            volumeStoragePoolUri    = volume['volumeStoragePoolUri']
            volumeUri               = volume['volumeUri']
            volumeStorageSystemUri  = volume['volumeStorageSystemUri']
            scriptCode.append("volume.update(volumeStorageSystemUri                     = {}    )".format(build_uri(volumeStorageSystemUri))            )
            if volumeUri:
                scriptCode.append("volume.update(volumeUri                                  = {}    )".format(build_uri(volumeUri))                     )
            
            # find on storage pools
            storage_pools           = oneview_client.storage_pools.get_all(filter='isManaged=True')
            for pool in storage_pools:
                pool_name = ''
                if  volumeStoragePoolUri == pool['uri']:
                    pool_name = pool['name']
            if pool_name:
                scriptCode.append("        pool_name = \'{}\'".format(pool_name)                                                                        )
                scriptCode.append("        storage_pools  = oneview_client.storage_pools.get_all(filter=\'isManaged=True\')"                            )
                scriptCode.append("        for pool in storage_pools:"                                                                                  )
                scriptCode.append("            if pool_name == pool[\'name\']:"                                                                         )
                scriptCode.append("                 volume.update(volumeStoragePoolUri   = pool[\'uri\']"                                               )
         
                      
            
            
            #if 'Manual' in lunType:

            scriptCode.append("volumeAttachments.append(volume)"                                                                                        )            

    
    
    
    
    
    scriptCode.append(CR)
    scriptCode.append("print(json.dumps(PROFILE, indent=4))"                                                                                            ) 
    scriptCode.append(CR)
    scriptCode.append("#  Creating {0} ---> {1} ".format(category,name)                                                                                 )
    if 'server-profile-templates' in category:
        scriptCode.append("spt      = oneview_client.server_profile_templates.create(PROFILE)"                                                          )                 
    else:
        scriptCode.append("sp      = oneview_client.server_profiles.create(PROFILE)"                                                                    ) 


                                                                                 
# ================================================================================================
#
#   generate_server_profile_templates_script
#
# ================================================================================================
def generate_server_profile_templates_script(to_file):
    
    scriptCode                  = []
    build_import_files(scriptCode)
    build_constants(scriptCode)
    build_config(scriptCode)

    
    server_profile_templates = oneview_client.server_profile_templates.get_all()


    for prof in server_profile_templates:
        category                            = prof["category"]
        name                                = prof["name"]  
        serverProfileDescription            = prof["serverProfileDescription"]
        

        scriptCode.append(CR)
        scriptCode.append("#===================Attributes for {0} {1} ========================".format(category,name)                                   )
        scriptCode.append("PROFILE                                      = dict()"                                                                       )
        scriptCode.append("PROFILE.update(name                          = \'{}\')".format(name)                                                         )

        generate_profile_or_templates_script(scriptCode, prof )


    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)


                                                                                 
# ================================================================================================
#
#   generate_server_profiles_script
#
# ================================================================================================
def generate_server_profiles_script(to_file):
    
    scriptCode                              = []
    build_import_files(scriptCode)
    build_constants(scriptCode)
    build_config(scriptCode)


    server_profiles                         = oneview_client.server_profiles.get_all()

    for prof in server_profiles:
        category                            = prof["category"]
        name                                = prof["name"]
        serverHardwareUri                   = prof["serverHardwareUri"]
        serverProfileTemplateUri            = prof["serverProfileTemplateUri"]

    
        scriptCode.append(CR)
        scriptCode.append("#===================Attributes for {0} {1} ========================".format(category,name)                                   )

        scriptCode.append("PROFILE                                      = dict()"                                                                       )
        scriptCode.append("PROFILE.update(name                          = \'{}\')".format(name)                                                         )

        ### Server Hardware
        if serverHardwareUri:
            s_name = ""
            for s in oneview_client.server_hardware.get_all():
                if serverHardwareUri in s['uri']:
                    s_name = s['name'] 
            scriptCode.append("s_name                                       = \'{}\'".format(s_name)                                                     )
            scriptCode.append("servers = oneview_client.server_hardware.get_all()"                                                                       )
            scriptCode.append("s_uri   = \'\'"                                                                                                           )
            scriptCode.append("for s in servers:"                                                                                                        )
            scriptCode.append("     if s_name in s[\'name\']:"                                                                                           )
            scriptCode.append("         s_uri = s[\'uri\']"                                                                                              )
            scriptCode.append("PROFILE.update(serverHardwareUri             = s_uri)"                                                                    )
        else:       # unassigned
            scriptCode.append("PROFILE.update(serverHardwareUri             = \'\')"                                                                     )
        


        ### Server profile Template
        if serverProfileTemplateUri:
            spt_name = ""
            for spt in oneview_client.server_profile_templates.get_all():
                if  serverProfileTemplateUri in spt['uri']:
                    spt_name    = spt['name']
            scriptCode.append("spt_name                                     = \'{}\'".format(spt_name)                                                  )
            scriptCode.append("spt_uri   = \'\'"                                                                                                        )
            scriptCode.append("for spt in oneview_client.server_profile_templates.get_all():"                                                           )
            scriptCode.append("     if spt_name in spt[\'name\']:"                                                                                      )
            scriptCode.append("         spt_uri     = spt[\'uri\']"                                                                                     )
            scriptCode.append("         this_spt    = spt "                                                                                             )
            scriptCode.append("PROFILE.update(serverProfileTemplateUri      = spt_uri)"                                                                 )

            # Structure attributes
            scriptCode.append("PROFILE.update(firmware                      = copy.deepcopy(this_spt[\'firmware\']))"                                   )
            scriptCode.append("PROFILE.update(boot                          = copy.deepcopy(this_spt[\'boot\']))"                                       )
            scriptCode.append("PROFILE.update(bootMode                      = copy.deepcopy(this_spt[\'bootMode\']))"                                   )
            scriptCode.append("PROFILE.update(bios                          = copy.deepcopy(this_spt[\'bios\']))"                                       )
            scriptCode.append("PROFILE.update(localStorage                  = copy.deepcopy(this_spt[\'localStorage\']))"                               )
            scriptCode.append("PROFILE.update(sanStorage                    = copy.deepcopy(this_spt[\'sanStorage\']))"                                 )
            scriptCode.append("PROFILE.update(osDeploymentSettings          = copy.deepcopy(this_spt[\'osDeploymentSettings\']))"                       )
            scriptCode.append("PROFILE.update(connections                   = copy.deepcopy(this_spt[\'connectionSettings\'][\'connections\']))"        )

            # Single value attribute
            scriptCode.append("PROFILE.update(description                   = copy(this_spt[\'description\']))"                                         )
            scriptCode.append("PROFILE.update(affinity                      = copy(this_spt[\'affinity\']))"                                            )
            scriptCode.append("PROFILE.update(wwnType                       = copy(this_spt[\'wwnType\']))"                                             )
            scriptCode.append("PROFILE.update(macType                       = copy(this_spt[\'macType\']))"                                             )
            scriptCode.append("PROFILE.update(serialNumberType              = copy(this_spt[\'serialNumberType\']))"                                    )
            scriptCode.append("PROFILE.update(iscsiInitiatorNameType        = copy(this_spt[\'iscsiInitiatorNameType\']))"                              )
            scriptCode.append("PROFILE.update(hideUnusedFlexNics            = copy(this_spt[\'hideUnusedFlexNics\']))"                                  )
            
        else:   # Server profile created manually
            generate_profile_or_templates_script(scriptCode, prof)




    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)



#MAIN
oneview_client  = OneViewClient(CONFIG)

#--- ethernet networks
to_file         = "ov_ethernet_networks.py"
print(CR)
print("Generating python script file ====>      {}".format(to_file)                 )
generate_ethernet_networks_script(to_file)

#--- fc networks
to_file         = "ov_fc_networks.py"
print(CR)
print("Generating python script file ====>      {}".format(to_file)                 )
generate_fc_networks_script(to_file)

#--- fcoe networks
to_file         = "ov_fcoe_networks.py"
print(CR)
print("Generating python script file ====>      {}".format(to_file)                 )
generate_fcoe_networks_script(to_file)

#--- network sets
to_file         = "ov_network_sets.py"
print(CR)
print("Generating python script file ====>      {}".format(to_file)                 )
generate_network_sets_script(to_file)

#--- ligs
to_file         = "ov_logical_interconnect_groups.py"
print(CR)
print("Generating python script file ====>      {}".format(to_file)                 )
generate_logical_interconnect_groups_script(to_file)

#--- SAS ligs
to_file         = "ov_sas_logical_interconnect_groups.py"
print(CR)
print("Generating python script file ====>      {}".format(to_file)                 )
generate_sas_logical_interconnect_groups_script(to_file)

#--- enclosure groups
to_file         = "ov_enclosure_groups.py"
print(CR)
print("Generating python script file ====>      {}".format(to_file)                 )
generate_enclosure_groups_script(to_file)


#--- Profile templates
to_file         = "ov_server_profile_templates.py"
print(CR)
print("Generating python script file ====>      {}".format(to_file)                 )
generate_server_profile_templates_script(to_file)

#--- Profiles
to_file         = "ov_server_profiles.py"
print(CR)
print("Generating python script file ====>      {}".format(to_file)                 )
generate_server_profiles_script(to_file) 


