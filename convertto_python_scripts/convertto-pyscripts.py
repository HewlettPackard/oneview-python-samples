from pprint import pprint
import json
import copy
import os
from os import sys


from hpOneView.exceptions import HPOneViewException
from hpOneView.oneview_client import OneViewClient

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)




TABSPACE         = "    "
COMMA           = ','
CR              = '\n'




    

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

    if '/os-deployment-plans/' in sourceUri:
        res                 = oneview_client.os_deployment_plans.get(sourceUri)
        res_name            = res['name']
        dest_uri            = "oneview_client.os_deployment_plans.get_by(\'name\', \'{0}\')[0][\'uri\']".format(res_name)
    if '/enclosure-groups/' in sourceUri:
        res                 = oneview_client.enclosure_groups.get_by_uri(sourceUri)
        res_name            = res.data['name']
        dest_uri            = "oneview_client.enclosure_groups.get_by_name(\'{0}\').data[\'uri\']".format(res_name)

    if '/sas-logical-interconnect-groups/' in sourceUri:
        sas_ligs            = oneview_client.sas_logical_interconnect_groups.get_all()
        for sas_lig in sas_ligs:
            if sourceUri in sas_lig['uri']:
                res_name    = sas_lig['name']
                dest_uri    = "oneview_client.sas_logical_interconnect_groups.get_by_name(\'{0}\').data[\'uri\']".format(res_name)
                
    if '/logical-interconnect-groups/' in sourceUri:
        res                 = oneview_client.logical_interconnect_groups.get_by_uri(sourceUri)
        res_name            = res.data['name']
        dest_uri            = "oneview_client.logical_interconnect_groups.get_by(\'name\', \'{0}\')[0][\'uri\']".format(res_name)

    if '/ethernet-networks/' in sourceUri:
        res                 = oneview_client.ethernet_networks.get_by_uri(sourceUri)
        res_name            = res.data['name']
        dest_uri            = "oneview_client.ethernet_networks.get_by(\'name\', \'{0}\')[0][\'uri\']".format(res_name)
    if '/fc-networks/' in sourceUri:
        res                 = oneview_client.fc_networks.get_by_uri(sourceUri)
        res_name            = res.data['name']
        dest_uri            = "oneview_client.fc_networks.get_by(\'name\', \'{0}\')[0][\'uri\']".format(res_name)
    if '/fcoe-networks/' in sourceUri:
        res                 = oneview_client.fcoe_networks.get(sourceUri)
        res_name            = res['name']
        dest_uri            = "oneview_client.fcoe_networks.get_by(\'name\', \'{0}\')[0][\'uri\']".format(res_name) 
    if '/network-sets/' in sourceUri:
        network_sets        = oneview_client.network_sets.get_all()
        for ns in network_sets:
            if sourceUri in ns['uri']:
                res = ns
        res_name            = res['name']
        dest_uri            = "oneview_client.network_sets.get_by(\'name\', \'{0}\')[0][\'uri\']".format(res_name)

    if '/enclosures/' in sourceUri:
        res                 = oneview_client.enclosures.get_by_uri(sourceUri)
        res_name            = res.data['name']
        dest_uri            = "oneview_client.enclosures.get_by_name(\'{0}\').data[\'uri\']".format(res_name) 
    if '/server-hardware-types/' in sourceUri:
        res                 = oneview_client.server_hardware_types.get_by_uri(sourceUri)
        res_name            = res.data['name']
        dest_uri            = "oneview_client.server_hardware_types.get_by_name(\'{0}\').data[\'uri\']".format(res_name) 
    if '/server-hardware/' in sourceUri:
        res                 = oneview_client.server_hardware.get_by_uri(sourceUri)
        res_name            = res.data['name']
        dest_uri            = "oneview_client.server_hardware.get_by_name(\'{0}\').data[\'uri\']".format(res_name) 
    if '/server-profile-templates/' in sourceUri:
        res                 = oneview_client.server_profile_templates.get_by_uri(sourceUri)
        res_name            = res.data['name']
        dest_uri            = "oneview_client.server_profile_templates.get_by_name(\'{0}\').data[\'uri\']".format(res_name) 
    if '/server-profiles/' in sourceUri:
        res                 = oneview_client.server_profiles.get_by_uri(sourceUri)
        res_name            = res.data['name']
        dest_uri            = "oneview_client.server_profiles.get_by_name(\'{0}\').data[\'uri\']".format(res_name) 

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


    scriptCode.append("import requests"                                                                                                             )
    scriptCode.append("import urllib3"                                                                                                              )
    scriptCode.append("urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)"                                                         )

    scriptCode.append(CR)
# ================================================================================================
#
#   Build constants
#
# ================================================================================================
def build_constants(scriptCode):
    scriptCode.append("TABSPACE                                     = \'    \'"                                                                     )    
    scriptCode.append("COMMA                                        = \',\'"                                                                        )
    scriptCode.append("CR                                           = \'\\n\'"                                                                      )  
    scriptCode.append(CR)                        

# ================================================================================================
#
#   Build config.json and OV connection
#
# ================================================================================================
def build_config(scriptCode,config_dest_file):

    
    scriptCode.append(CR)
    scriptCode.append("#===================Connect to OneView ========================"                                                             ) 
    scriptCode.append("print(CR)"                                                                                                                   )  
    scriptCode.append("print \'#===================Connect to OneView ========================\'"                                                   ) 
    scriptCode.append("print(CR)"                                                                                                                   )  
    scriptCode.append("with open(\'{}\') as json_data:               ".format(config_dest_file)                                                     )
    scriptCode.append("     config = json.load(json_data)            "                                                                              )
    scriptCode.append("     oneview_client = OneViewClient(config)   "                                                                              )    
         
    # Build session ID
    scriptCode.append("ovIP                          = config[\'ip\']"                                                                              )
    scriptCode.append("ovAPI                         = config[\'api_version\']"                                                                     )
    scriptCode.append("ovUser                        = config[\'credentials\'][\'userName\']"                                                       )
    scriptCode.append("ovPassword                    = config[\'credentials\'][\'password\']"                                                       )
    # Get OneView credentials for REST API calls
    scriptCode.append("cred                          = dict() "                                                                                     )
    scriptCode.append("cred.update(userName          = \'{}\'.format(ovUser) )"                                                                     )
    scriptCode.append("cred.update(password          = \'{}\'.format(ovPassword) )"                                                                 )
    # POST REST to get sesion ID
    scriptCode.append("auth_uri                      = \'https://{}/rest/login-sessions\'.format(ovIP)"                                             )    
    scriptCode.append("headers                       = { "                                                                                          )
    scriptCode.append("    \'content-type\': \'application/json\',"                                                                                 )
    scriptCode.append("    \'X-Api-Version': \'{}\'  .format(ovAPI)"                                                                                )
    scriptCode.append("}                                "                                                                                           ) 
    scriptCode.append("resp = requests.post(auth_uri, headers=headers, timeout=60, verify=False,data=json.dumps(cred))"                             )
    # Format the response to extract sessionID
    scriptCode.append("token                         = json.loads(resp.text) "                                                                      )
    scriptCode.append("sessionID                     = token[\'sessionID\'] "                                                                       )

    # Add session ID to headers
    scriptCode.append("headers.update(Auth           = \'{}\' .format(sessionID) )"                                                                 )


    scriptCode.append(CR)
    scriptCode.append(CR)

# ================================================================================================
#
#  Build function to update bandwdith 
#
# ================================================================================================
def build_function_to_update_bandwidth(scriptCode):
    scriptCode.append(CR)
    scriptCode.append(CR)

    scriptCode.append("# ================================================================================================"                        )
    scriptCode.append("#                                                                                                 "                        )
    scriptCode.append("#  Function to update bandwdith                                                                   "                        )
    scriptCode.append("#                                                                                                 "                        )
    scriptCode.append("# ================================================================================================"                        )
    
    scriptCode.append("def update_bandwidth(connectionTemplateUri, ovIP, headers, typicalBandwidth, maximumBandwidth):"                           )
    scriptCode.append("     connectionTemplateUri    = 'https://{0}{1}'.format(ovIP,connectionTemplateUri)"                                       )
    scriptCode.append("     resp                     = requests.get(connectionTemplateUri, headers=headers, timeout=60, verify=False) "           )
    scriptCode.append("     this_con_template        = json.loads(resp.text)"                                                                     )
    scriptCode.append("     this_con_template['bandwidth'].update(maximumBandwidth   = \'{}\'.format(maximumBandwidth))"                              )                     
    scriptCode.append("     this_con_template['bandwidth'].update(typicalBandwidth   = \'{}\'.format(typicalBandwidth))"                              )
    scriptCode.append("     resp = requests.put(connectionTemplateUri, data = json.dumps(this_con_template), headers=headers, timeout=60, verify=False)" )
    scriptCode.append(CR)
    scriptCode.append(CR)

# ================================================================================================
#
#  Build function to uodate scope
#
# ================================================================================================
def build_function_to_update_scope(scriptCode):
    scriptCode.append(CR)
    scriptCode.append(CR)

    scriptCode.append("# ================================================================================================"                        )
    scriptCode.append("#                                                                                                 "                        )
    scriptCode.append("#  Function to update scope for OV resource                                                       "                        )
    scriptCode.append("#                                                                                                 "                        )
    scriptCode.append("# ================================================================================================"                        )

    
    scriptCode.append("def update_scope(scopeNames, resourceUri):                      "                                                          )
    scriptCode.append("     for sc_name in scopeNames:                                 "                                                          )
    scriptCode.append("         scope           = oneview_client.scopes.get_by_name(sc_name) "                                                    )
    scriptCode.append("         if scope:                                              "                                                          )
    scriptCode.append("             OPTIONS     = []                                   "                                                          )
    scriptCode.append("             OPTIONS.append(resourceUri )                       "                                                          )
    scriptCode.append("             oneview_client.scopes.patch(scope[\'uri\'], \'add\', \'/addedResourceUris\', OPTIONS)"                        )
    scriptCode.append(CR)
    scriptCode.append(CR)


# ================================================================================================
#
#  Get scope names
#
# ================================================================================================
def get_scope_names(scopesUri,ovIP,headers):

    scopeNames          = []
    urn                 = 'https://{0}/{1}'.format(ovIP,scopesUri)
    resp                = requests.get(urn, headers=headers, timeout=60, verify=False)
    data                = json.loads(resp.text) 
    for scope_uri in data['scopeUris']: 
        scope           = oneview_client.scopes.get(scope_uri) 
        if scope:                                              
            scopeNames.append(scope['name'])

    return scopeNames

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
    build_function_to_update_bandwidth(scriptCode)
    build_function_to_update_scope(scriptCode)
    build_config(scriptCode, config_file_dest)


    scriptCode.append("print(CR)"                                                                                                                                 ) 
    scriptCode.append("print(\'#===================Generate ethernet networks ========================\')"                                                        )  
    scriptCode.append("print(CR)"                                                                                                                                 )      
    ethernet_nets           = oneview_client.ethernet_networks.get_all()
    connection_templates    = oneview_client.connection_templates.get_all()

    for net in ethernet_nets:
        _type                   = net["type"]
        name                    = net["name"]
        description             = net["description"]
        purpose                 = net["purpose"]
        etherType               = net["ethernetNetworkType"]
        vlanId                  = net["vlanId"]
        smartLink               = net["smartLink"]
        privateNetwork          = net["privateNetwork"]
        connectionTemplateUri   = net['connectionTemplateUri']
        ethernetNetworkType     = net['ethernetNetworkType']

        ### Scopes
        scopesUri                = net['scopesUri']
        if scopesUri:
            scopesName           = get_scope_names(scopesUri, ovIP, headers)

        tBandwidth              = ''
        mBandwidth              = ''
        for ct in connection_templates:
            if connectionTemplateUri == ct['uri']:
                bandwidth    = ct['bandwidth']
                tBandwidth   = bandwidth['typicalBandwidth']
                mBandwidth   = bandwidth['maximumBandwidth']


        scriptCode.append(CR)
        scriptCode.append("res          = oneview_client.ethernet_networks.get_by(\'name\', \'{0}\') ".format(name)                                          )
        scriptCode.append("if not res:                                                               "                                                       )  
        scriptCode.append("     #===================Attributes for network {} ========================".format(name)                                         )
        scriptCode.append("     print(\'---------Creating network {}\')                               ".format(name)                                         )                                                                                                                                                                                
        scriptCode.append("     ETHERNET_NETWORK                                             = dict()"                                                       )
        scriptCode.append("     ETHERNET_NETWORK.update(type                                 = \'{}\')".format(_type)                                        )
        scriptCode.append("     ETHERNET_NETWORK.update(name                                 = \'{}\')".format(name)                                         )
        if description is not None:
            scriptCode.append("     ETHERNET_NETWORK.update(description                          = \'{}\')".format(description)                              )
        scriptCode.append("     ETHERNET_NETWORK.update(purpose                              = \'{}\')".format(purpose)                                      )
        scriptCode.append("     ETHERNET_NETWORK.update(ethernetNetworkType                  = \'{}\')".format(ethernetNetworkType)                          )

        if etherType == 'Tagged':
            scriptCode.append("     ETHERNET_NETWORK.update(vlanId                               = {})".format(vlanId)                                       )
        
        scriptCode.append("     ETHERNET_NETWORK.update(smartLink                            = \'{}\')".format(smartLink)                                    )
        scriptCode.append("     ETHERNET_NETWORK.update(privateNetwork                       = \'{}\')".format(privateNetwork)                               )


        scriptCode.append("     # Create Ethernet network {}".format(name)                                                                                   )
        scriptCode.append("     net                      = oneview_client.ethernet_networks.create(ETHERNET_NETWORK)"                                        )
        # New OV resource is created - get its URI to update scope / bandwidth
        # Update scope
        scriptCode.append("     resourceUri  = net.data[\'uri\']                                        "                                                    )
        if scopesName:
            scriptCode.append("     update_scope({}, resourceUri)                                       " .format(scopesName)                                )
        # Update bandwidth
        scriptCode.append("     connectionTemplateUri    = net.data[\'connectionTemplateUri\']"                                                              )
        scriptCode.append("     update_bandwidth(connectionTemplateUri, ovIP, headers, {0}, {1})".format(tBandwidth,mBandwidth)                              )  

        scriptCode.append("else:"                                                                                                                            )
        scriptCode.append("     res_name     = res[0][\'name\']                                         "                                                    )   
        scriptCode.append("     print \'network ---> \' + res_name + \' already exists. Skip creating it.....\' "                                            )
    scriptCode.append(CR)


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
    build_function_to_update_bandwidth(scriptCode)
    build_function_to_update_scope(scriptCode)
    build_config(scriptCode, config_file_dest)

    scriptCode.append("print(\'#===================Generate fc networks ========================\')"                                                              )  
    scriptCode.append("print(CR)"                                                                                                                                 )      
        
    fc_nets              = oneview_client.fc_networks.get_all()
    connection_templates = oneview_client.connection_templates.get_all()
    for net in fc_nets:
        _type                   = net["type"]
        name                    = net["name"]
        description             = net["description"]
        fabricType              = net["fabricType"]
        autoLoginRedistribution = net["autoLoginRedistribution"]
        linkStabilityTime       = net["linkStabilityTime"]
        managedSanUri           = net["managedSanUri"]
        connectionTemplateUri   = net['connectionTemplateUri']

        ### Scopes
        scopesUri                = net['scopesUri']
        if scopesUri:
            scopesName           = get_scope_names(scopesUri, ovIP, headers)

        scriptCode.append(CR)
        scriptCode.append("res          = oneview_client.fc_networks.get_by(\'name\', \'{0}\') ".format(name)                                                )   
        scriptCode.append("if not res:                                                           "                                                           )  
        scriptCode.append("     #===================Attributes for network {} ========================".format(name)                                         )
        scriptCode.append("     print(\'---------Creating FC network {}\')                            ".format(name)                                         )  
        scriptCode.append("     FC_NETWORK                                                   = dict()"                                                       )
        scriptCode.append("     FC_NETWORK.update(type                                       = \'{}\')".format(_type)                                        )
        scriptCode.append("     FC_NETWORK.update(name                                       = \'{}\')".format(name)                                         )
        if description is not None:
            scriptCode.append("     FC_NETWORK.update(description                                = \'{}\')".format(description)                              )

        scriptCode.append("     FC_NETWORK.update(fabricType                                 = \'{}\')".format(fabricType)                                   )
        scriptCode.append("     FC_NETWORK.update(autoLoginRedistribution                    = \'{}\')".format(autoLoginRedistribution)                      )
        scriptCode.append("     FC_NETWORK.update(linkStabilityTime                          = \'{}\')".format(linkStabilityTime)                            )


        # TBD - Also make sure thate endDict is here
        # if managedSanUri is not None:
        #    scriptCode.append("FC_NETWORK.update(managedSanUri= \'{}\')".format(managedSanUri))
        

        for ct in connection_templates:
            if connectionTemplateUri == ct['uri']:
                bandwidth    = ct['bandwidth']
                tBandwidth   = bandwidth['typicalBandwidth']
                mBandwidth   = bandwidth['maximumBandwidth']



        scriptCode.append("     # Create FC network {}".format(name)                                                                                         )
        scriptCode.append("     net                      = oneview_client.fc_networks.create(FC_NETWORK)"                                                    )
        # New OV resource is created - get its URI to update scope / bandwidth
        # Update scope
        scriptCode.append("     resourceUri  = net.data[\'uri\']                                        "                                                    )
        if scopesName:
            scriptCode.append("     update_scope({}, resourceUri)                                       " .format(scopesName)                                )
        # Update bandwidth
        scriptCode.append("     connectionTemplateUri    = net.data[\'connectionTemplateUri\']"                                                              )
        scriptCode.append("     update_bandwidth(connectionTemplateUri, ovIP, headers, {0}, {1})".format(tBandwidth,mBandwidth)                              )    

        scriptCode.append("else:"                                                                                                                            )
        scriptCode.append("     res_name     = res[0][\'name\']                                         "                                                    )
        scriptCode.append("     print \'network ---> \' + res_name + \' already exists. Skip creating it.....\' "                                            )
        
    scriptCode.append(CR)
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
    build_function_to_update_bandwidth(scriptCode)
    build_function_to_update_scope(scriptCode)
    build_config(scriptCode, config_file_dest)

    scriptCode.append("print(\'#===================Generate fcoe networks ========================\')"                                                            )  
    scriptCode.append("print(CR)"                                                                                                                                 )      
        
    fcoe_nets               = oneview_client.fcoe_networks.get_all()
    connection_templates    = oneview_client.connection_templates.get_all()

    for net in fcoe_nets:
        _type                   = net["type"]
        name                    = net["name"]
        description             = net["description"]
        vlanId                  = net["vlanId"]
        fabricUri               = net["fabricUri"]
        managedSanUri           = net["managedSanUri"]
        connectionTemplateUri   = net['connectionTemplateUri']

        ### Scopes
        scopesUri                = net['scopesUri']
        if scopesUri:
            scopesName           = get_scope_names(scopesUri, ovIP, headers)

        scriptCode.append(CR)

        scriptCode.append("res          = oneview_client.fcoe_networks.get_by(\'name\', \'{0}\') ".format(name)                                              )
        scriptCode.append("if not res:                                                               "                                                       )         
        scriptCode.append("     #===================Attributes for network {} ========================".format(name)                                         )
        scriptCode.append("     print(\'---------Creating FCOE network {}\')                          ".format(name)                                         )  
        scriptCode.append("     FCOE_NETWORK                                                 = dict()"                                                       )
        scriptCode.append("     FCOE_NETWORK.update(type                                     = \'{}\')".format(_type)                                        )
        scriptCode.append("     FCOE_NETWORK.update(name                                     = \'{}\')".format(name)                                         )
        if description is not None:
            scriptCode.append("     FCOE_NETWORK.update(description                              = \'{}\')".format(description)                              )

        scriptCode.append("     FCOE_NETWORK.update(vlanId                                   = {})".format(vlanId)                                           )

        # TBD - Also make sure thate endDict is here
        # if fabricUri is not None:
        #    scriptCode.append("FCOE_NETWORK.update(fabricUri    = \'{}\')".format(fabricUri))
        # if managedSanUri is not None:
        #    scriptCode.append("FCOE_NETWORK.update(managedSanUri    = \'{}\')".format(managedSanUri))


        for ct in connection_templates:
            if connectionTemplateUri == ct['uri']:
                bandwidth    = ct['bandwidth']
                tBandwidth   = bandwidth['typicalBandwidth']
                mBandwidth   = bandwidth['maximumBandwidth']



        scriptCode.append("     # Create FCOE network {}".format(name)                                                                                       )
        scriptCode.append("     net                      = oneview_client.fcoe_networks.create(FCOE_NETWORK)"                                                )
        # New OV resource is created - get its URI to update scope / bandwidth
        # Update scope
        scriptCode.append("     resourceUri  = net.data[\'uri\']                                        "                                                    )
        if scopesName:
            scriptCode.append("     update_scope({}, resourceUri)                                       " .format(scopesName)                                )
        # Update bandwidth
        scriptCode.append("     connectionTemplateUri    = net.data[\'connectionTemplateUri\']"                                                              )
        scriptCode.append("     update_bandwidth(connectionTemplateUri, ovIP, headers, {0}, {1})".format(tBandwidth,mBandwidth)                              )   
        scriptCode.append("else:"                                                                                                                            )
        scriptCode.append("     res_name     = res[0][\'name\']                                         "                                                    )
        scriptCode.append("     print \'network ---> \' + res_name + \' already exists. Skip creating it.....\' "                                            )
        
    scriptCode.append(CR)

    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)

# ================================================================================================
#
#   generate_network_sets_script
#
# ================================================================================================
def generate_network_sets_script(to_file):
    scriptCode   = []
    build_import_files(scriptCode)
    build_constants(scriptCode)
    build_function_to_update_bandwidth(scriptCode)
    build_function_to_update_scope(scriptCode)
    build_config(scriptCode, config_file_dest)

    scriptCode.append("print(\'#===================Generate network sets ========================\')"                                                )  
    scriptCode.append("print(CR)"                                                                                                                   )      
  
    network_sets         = oneview_client.network_sets.get_all_without_ethernet()
    connection_templates = oneview_client.connection_templates.get_all()

    for netset in network_sets:
        _type                   = netset["type"]
        name                    = netset["name"]
        description             = netset["description"]
        nativeNetworkUri        = netset["nativeNetworkUri"]
        networkUris             = netset["networkUris"]
        connectionTemplateUri   = netset['connectionTemplateUri']



        ### Scopes
        scopesUri               = netset['scopesUri']
        if scopesUri:
            scopesName          = get_scope_names(scopesUri, ovIP, headers)

        for ct in connection_templates:
            if connectionTemplateUri == ct['uri']:
                bandwidth    = ct['bandwidth']
                tBandwidth   = bandwidth['typicalBandwidth']
                mBandwidth   = bandwidth['maximumBandwidth']



        #nativeNet_dest  = oneview_client.ethernet_networks.get_by('name', nativeNetName)

        scriptCode.append(CR)
        scriptCode.append("res          = oneview_client.network_sets.get_by(\'name\', \'{0}\') ".format(name)                                               )
        scriptCode.append("if not res:                                                                    "                                                  )  

        scriptCode.append("     #===================Attributes for network set {} ========================".format(name)                                     )
        scriptCode.append("     print(\'---------Creating network set {}\')                               ".format(name)                                     )  
        scriptCode.append("     NETWORK_SET                                                  = dict()"                                                       )
        scriptCode.append("     NETWORK_SET.update(type                                      = \'{}\')".format(_type)                                        )
        scriptCode.append("     NETWORK_SET.update(name                                      = \'{}\')".format(name)                                         )
        if description is not None:
            scriptCode.append("     NETWORK_SET.update(description                               = \'{}\')".format(description)                              )

        scriptCode.append("     NETWORK_SET.update(networkUris                               = [])"                                                          )
        for _net_uri in networkUris:
            net_uri             = build_uri(_net_uri)   
            scriptCode.append("     NETWORK_SET[\'networkUris\'].append({})".format(net_uri)                                                                 )          


 

        scriptCode.append("     # Create network set {}".format(name)                                                                                        )
        scriptCode.append("     net                      = oneview_client.network_sets.create(NETWORK_SET)"                                                  )
        # New OV resource is created - get its URI to update scope / bandwidth
        # Update scope
        scriptCode.append("     resourceUri  = net[\'uri\']                                        "                                                         )
        if scopesName:
            scriptCode.append("     update_scope({}, resourceUri)                                       " .format(scopesName)                                )
        # Update bandwidth
        scriptCode.append("     connectionTemplateUri    = net[\'connectionTemplateUri\']"                                                                   )
        scriptCode.append("     update_bandwidth(connectionTemplateUri, ovIP, headers, {0}, {1})".format(tBandwidth,mBandwidth)                              )  

        scriptCode.append("else:"                                                                                                                            )
        scriptCode.append("     res_name     = res[0][\'name\']                                                "                                             )   
        scriptCode.append("     print \'network ---> \' + res_name + \' already exists. Skip creating it.....\' "                                            )
    scriptCode.append(CR)

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
    build_function_to_update_scope(scriptCode)
    build_config(scriptCode, config_file_dest)
    

    logical_interconnect_groups = oneview_client.logical_interconnect_groups.get_all()
 
    for lig in logical_interconnect_groups:
        _type                       = lig["type"]
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

        ### Scopes
        scopesUri                   = lig['scopesUri']
        if scopesUri:
            scopesName              = get_scope_names(scopesUri, ovIP, headers)

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
        scriptCode.append("res          = oneview_client.logical_interconnect_groups.get_by(\'name\', \'{0}\') ".format(name)                                )
        scriptCode.append("if not res:                                                                    "                                                  )  
        scriptCode.append("     #===================Attributes for Logical Interconnect Group {} ========================".format(name)                      )
        scriptCode.append("     print(\'---------Creating logical Interconnect Group {}\')                               ".format(name)                      )  
        scriptCode.append("     LOGICAL_INTERCONNECT_GROUP                                   = dict()"                                                       )
        scriptCode.append("     LOGICAL_INTERCONNECT_GROUP.update(type                       = \'{}\')".format(_type)                                        )
        scriptCode.append("     LOGICAL_INTERCONNECT_GROUP.update(name                       = \'{}\')".format(name)                                         )
        if description is not None:
            scriptCode.append("     LOGICAL_INTERCONNECT_GROUP.update(description                = \'{}\')".format(description)                              )
        scriptCode.append("     LOGICAL_INTERCONNECT_GROUP.update(enclosureType              = \'{}\')".format(enclosureType)                                )
        scriptCode.append("     LOGICAL_INTERCONNECT_GROUP.update(redundancyType             = \'{}\')".format(redundancyType)                               )
        scriptCode.append("     LOGICAL_INTERCONNECT_GROUP.update(interconnectBaySet         = {})".format(interconnectBaySet)                               ) 

        # ethernetSettings
        if -1 not in enclosureIndexes:                          # Check if not VC-FC
            scriptCode.append(CR + "     ##### ethernetSettings region"                                                                                      )
            scriptCode.append("     LOGICAL_INTERCONNECT_GROUP.update(ethernetSettings           = dict() )"                                                 )
            scriptCode.append("     ethernetSettings                                             = LOGICAL_INTERCONNECT_GROUP[\'ethernetSettings\']"         )
            scriptCode.append("     ethernetSettings.update(type                                 = \'{}\')".format(ethernetSettingsType)                     )
            scriptCode.append("     ethernetSettings.update(enableIgmpSnooping                   = \'{}\')".format(igmpSnooping)                             )
            scriptCode.append("     ethernetSettings.update(igmpIdleTimeoutInterval              = \'{}\')".format(igmpIdleTimeout)                          )
            scriptCode.append("     ethernetSettings.update(enableNetworkLoopProtection          = \'{}\')".format(networkLoopProtection)                    )
            scriptCode.append("     ethernetSettings.update(enablePauseFloodProtection           = \'{}\')".format(pauseFloodProtection)                     )
            scriptCode.append("     ethernetSettings.update(enableRichTLV                        = \'{}\')".format(enableRichTLV)                            )
            scriptCode.append("     ethernetSettings.update(enableTaggedLldp                     = \'{}\')".format(taggedLldp)                               )
            scriptCode.append("     ethernetSettings.update(enableFastMacCacheFailover           = \'{}\')".format(fastMacCacheFailover)                     )
            scriptCode.append("     ethernetSettings.update(macRefreshInterval                   = \'{}\')".format(macRefreshInterval)                       )
            scriptCode.append("     ethernetSettings.update(lldpIpv4Address                      = \'{}\')".format(lldpIpv4Address)                          )
            scriptCode.append("     ethernetSettings.update(lldpIpv6Address                      = \'{}\')".format(lldpIpv6Address)                          )


        # Enclosure Indexes

        scriptCode.append(CR + "     ##### enclosure Indexes region"                                                                                         )
        scriptCode.append("     indexArray                                                  = []"                                                            )
        for index in enclosureIndexes:
            scriptCode.append("     indexArray.append({})".format(index)                                                                                     )
        
        scriptCode.append("     LOGICAL_INTERCONNECT_GROUP.update(enclosureIndexes          = [])"                                                           )
        scriptCode.append("     for index in indexArray:"                                                                                                    )
        scriptCode.append("          LOGICAL_INTERCONNECT_GROUP[\'enclosureIndexes\'].append(index)"                                                         )


        # InterConnect Map Templates
        scriptCode.append(CR + "     ##### InterConnect Map Templates region"                                                                                )
        scriptCode.append("     LOGICAL_INTERCONNECT_GROUP.update(interconnectMapTemplate   = dict())"                                                       )
        scriptCode.append("     LOGICAL_INTERCONNECT_GROUP[\'interconnectMapTemplate\'].update(interconnectMapEntryTemplates = [])"                          )
        scriptCode.append("     interconnectMapEntryTemplates = LOGICAL_INTERCONNECT_GROUP[\'interconnectMapTemplate\'][\'interconnectMapEntryTemplates\']"  )
                                                                
        for mapEntryTemplate in ICmapEntryTemplates:
            logicalLocation         = mapEntryTemplate["logicalLocation"]
            scriptCode.append("     map_entry_template                                           = dict()"                                                   )           
            scriptCode.append("     map_entry_template.update(logicalLocation                    = dict())"                                                  )  
            scriptCode.append("     logicalLocation                                              = map_entry_template[\'logicalLocation\']"                  )    
            scriptCode.append("     location_entries                                             = []"                                                       )     
            for entry in logicalLocation["locationEntries"]:
                relativeValue       = entry["relativeValue"]
                _type               = entry["type"]
                if "Enclosure" == _type:
                    enclosureIndex  = relativeValue
                scriptCode.append(CR                                                                                                                         )
                scriptCode.append("     location_entry                                               = dict()"                                               )
                scriptCode.append("     location_entry.update(relativeValue                          = {})".format(relativeValue)                            )
                scriptCode.append("     location_entry.update(type                                   = \'{}\')".format(_type)                                )
                scriptCode.append("     location_entries.append(location_entry)"                                                                             )
                scriptCode.append("     logicalLocation.update(locationEntries                       = location_entries)"                                    )

            scriptCode.append("     map_entry_template.update(enclosureIndex                     = {})".format(enclosureIndex)                               ) 
            
            icTypeUri                   =  mapEntryTemplate["permittedInterconnectTypeUri"] 
            if icTypeUri is not None:
                interconnects           = oneview_client.interconnect_types.get_all()
                icName                  = ''
                for ic in interconnects:
                    if icTypeUri in ic['uri']:
                        icName = ic['name']
                if icName:
                    scriptCode.append("     icTypeUri                                                    = oneview_client.interconnect_types.get_by_name(\'{}\').data[\'uri\']".format(icName)  )
                    scriptCode.append("     map_entry_template.update(permittedInterconnectTypeUri       = icTypeUri)"                                       )

            scriptCode.append("     interconnectMapEntryTemplates.append(map_entry_template)"                                                                )

        # uplinksets
        scriptCode.append(CR + "     ##### Uplink Sets region"                                                                                               )
        scriptCode.append("     LOGICAL_INTERCONNECT_GROUP.update(uplinkSets                 = [])"                                                          )  
        
        for upl in uplinkSets:
            uplName                 = upl["name"]
            nativeNetworkUri        = upl["nativeNetworkUri"]
            networkUris             = upl["networkUris"]                # []
            networkType             = upl["networkType"]
            ethernetNetworkType     = upl["ethernetNetworkType"]
            lacpTimer               = upl["lacpTimer"]
            mode                    = upl["mode"]
            upl_logicalPortConfigs  = upl["logicalPortConfigInfos"]     #[]

    
    
            scriptCode.append("     upl_element                                                  = dict()"                                                   )
            scriptCode.append("     upl_element.update(name                                      = \'{}\')".format(uplName)                                  )
            scriptCode.append("     upl_element.update(networkType                               = \'{}\')".format(networkType)                              )
            scriptCode.append("     upl_element.update(mode                                      = \'{}\')".format(mode)                                     )
            if 'Ethernet' == networkType:
                scriptCode.append("     upl_element.update(ethernetNetworkType                       = \'{}\')".format(ethernetNetworkType)                  )
                scriptCode.append("     upl_element.update(lacpTimer                                 = \'{}\')".format(lacpTimer)                            )
            
            if nativeNetworkUri is not None:
                net_uri = build_netUri(networkType,nativeNetworkUri)  
                scriptCode.append("     upl_element.update(nativeNetworkUri                          = {})".format(net_uri)                                  )
            
            scriptCode.append("     upl_element.update(networkUris = [])"                                                                                    )
            for _net_uri in networkUris:
                net_uri             = build_uri(_net_uri) 
                scriptCode.append("     upl_element[\'networkUris\'].append({})".format(net_uri)                                                             )
    

            scriptCode.append("     upl_element.update(logicalPortConfigInfos = [])"                                                                         )
            scriptCode.append("     lpci_array                                                   = upl_element[\'logicalPortConfigInfos\']"                  )
            for upl_logical_port_config in upl_logicalPortConfigs:
                scriptCode.append("     lpci_element                                                 = dict()"                                               )
                scriptCode.append("     lpci_element.update(desiredSpeed                             = \'{}\')".format(upl_logical_port_config['desiredSpeed'])  )
                scriptCode.append("     lpci_element.update(logicalLocation                          = dict())"                                              )
                scriptCode.append("     lpci_element[\'logicalLocation\'].update(locationEntries   = [])"                                                    )
                upl_logicalLocation     = upl_logical_port_config['logicalLocation']

                for upl_entry in upl_logicalLocation["locationEntries"]:
                    upl_relativeValue       = upl_entry["relativeValue"]
                    upl_type                = upl_entry["type"]
                    scriptCode.append(CR                                                                                                                      )
                    scriptCode.append("     location_entry                                               = dict()"                                            )
                    scriptCode.append("     location_entry.update(relativeValue                          = {})".format(upl_relativeValue)                     )
                    scriptCode.append("     location_entry.update(type                                   = \'{}\')".format(upl_type)                          )
                    scriptCode.append("     lpci_element[\'logicalLocation\'][\'locationEntries\'].append(location_entry)"                                    )

                scriptCode.append("     lpci_array.append(lpci_element)"                                                                                      )
            
            # Add entry to  the uplinkSets array
            scriptCode.append("     LOGICAL_INTERCONNECT_GROUP[\'uplinkSets\'].append(upl_element)"                                                           )
            
        scriptCode.append(CR + "     ##### QOS - TBD"                                                                                                         )
        scriptCode.append(CR + "     ##### SNMP - TBD"                                                                                                        )
        
        
        
        scriptCode.append("")
        scriptCode.append("     #  Creating logical interconnect group "                                                                                    )
        scriptCode.append("     lig      = oneview_client.logical_interconnect_groups.create(LOGICAL_INTERCONNECT_GROUP)"                                   )
        # New OV resource is created - get its URI to update scope
        # Update scope
        scriptCode.append("     resourceUri  = lig.data[\'uri\']                                        "                                                        )
        if scopesName:
            scriptCode.append("     update_scope({}, resourceUri)                                       " .format(scopesName)                               )


        scriptCode.append("else:"                                                                                                                           )   
        scriptCode.append("     res_name     = res[0][\'name\']                                                "                                            )    
        scriptCode.append("     print \'lig ---> \' + res_name + \' already exists. Skip creating it.....\' "                                               )
    scriptCode.append(CR)
    
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
    build_function_to_update_scope(scriptCode)
    build_config(scriptCode, config_file_dest)
    
    
    logical_interconnect_groups = oneview_client.sas_logical_interconnect_groups.get_all()
 
    for lig in logical_interconnect_groups:
        _type                       = lig["type"]
        name                        = lig["name"]
        description                 = lig["description"] 
        enclosureType               = lig["enclosureType"]
        category                    = lig["category"]                    
        interconnectBaySet          = lig["interconnectBaySet"]
        enclosureIndexes            = lig["enclosureIndexes"] 

        ### Scopes
        scopesUri                   = lig['scopesUri']
        if scopesUri:
            scopesName              = get_scope_names(scopesUri, ovIP, headers)

        # Interconnect Map Templates
        ICmapTemplate               = lig["interconnectMapTemplate"]
        ICmapEntryTemplates         = ICmapTemplate["interconnectMapEntryTemplates"]        #[]
      


        scriptCode.append(CR)
        scriptCode.append("res          = oneview_client.sas_logical_interconnect_groups.get_by_name(\'{0}\') ".format(name)                                 )
        scriptCode.append("if not res:                                                                    "                                                  )  
        scriptCode.append("     #===================Attributes for SAS Logical Interconnect Group {} ========================".format(name)                  )
        scriptCode.append("     print(\'---------Creating SAS logical Interconnect Group {}\')                               ".format(name)                  )

        scriptCode.append("     SAS_LOGICAL_INTERCONNECT_GROUP                                   = dict()"                                                   )
        scriptCode.append("     SAS_LOGICAL_INTERCONNECT_GROUP.update(type                       = \'{}\')".format(_type)                                    )
        scriptCode.append("     SAS_LOGICAL_INTERCONNECT_GROUP.update(name                       = \'{}\')".format(name)                                     )
        if description is not None:
            scriptCode.append("     SAS_LOGICAL_INTERCONNECT_GROUP.update(description                = \'{}\')".format(description)                          )  
        scriptCode.append("     SAS_LOGICAL_INTERCONNECT_GROUP.update(enclosureType              = \'{}\')".format(enclosureType)                            )                              
        scriptCode.append("     SAS_LOGICAL_INTERCONNECT_GROUP.update(interconnectBaySet         = {})".format(interconnectBaySet)                           )

        
        scriptCode.append(CR + "     ##### enclosure Indexes region"                                                                                         )
        scriptCode.append("     indexArray                                                  = []"                                                            )
        for index in enclosureIndexes:
            scriptCode.append("     indexArray.append({})".format(index)                                                                                     )
        
        scriptCode.append("     SAS_LOGICAL_INTERCONNECT_GROUP.update(enclosureIndexes          = [])"                                                       )
        scriptCode.append("     for index in indexArray:"                                                                                                    )
        scriptCode.append("          SAS_LOGICAL_INTERCONNECT_GROUP[\'enclosureIndexes\'].append(index)"                                                     )   


        scriptCode.append(CR + "     ##### InterConnect Map Templates region"                                                                                )
        scriptCode.append("     SAS_LOGICAL_INTERCONNECT_GROUP.update(interconnectMapTemplate   = dict())"                                                   )
        scriptCode.append("     SAS_LOGICAL_INTERCONNECT_GROUP[\'interconnectMapTemplate\'].update(interconnectMapEntryTemplates = [])"                      )
        scriptCode.append("     interconnectMapEntryTemplates = SAS_LOGICAL_INTERCONNECT_GROUP[\'interconnectMapTemplate\'][\'interconnectMapEntryTemplates\']"  )
                                                                
        for mapEntryTemplate in ICmapEntryTemplates:
            logicalLocation         = mapEntryTemplate["logicalLocation"]
            scriptCode.append("     map_entry_template                                           = dict()"                                                   )           
            scriptCode.append("     map_entry_template.update(logicalLocation                    = dict())"                                                  )  
            scriptCode.append("     logicalLocation                                              = map_entry_template[\'logicalLocation\']"                  )    
            scriptCode.append("     location_entries                                             = []"                                                       )     
            for entry in logicalLocation["locationEntries"]:
                relativeValue       = entry["relativeValue"]
                _type               = entry["type"]
                if "Enclosure" == _type:
                    enclosureIndex  = relativeValue
                scriptCode.append(CR                                                                                                                         )
                scriptCode.append("     location_entry                                               = dict()"                                               )
                scriptCode.append("     location_entry.update(relativeValue                          = {})".format(relativeValue)                            )
                scriptCode.append("     location_entry.update(type                                   = \'{}\')".format(_type)                                )
                scriptCode.append("     location_entries.append(location_entry)"                                                                             )
                scriptCode.append("     logicalLocation.update(locationEntries                       = location_entries)"                                    )

            scriptCode.append("     map_entry_template.update(enclosureIndex                     = {})".format(enclosureIndex)                               ) 
            
            icTypeUri                   =  mapEntryTemplate["permittedInterconnectTypeUri"] 
            if icTypeUri is not None:
                
                icName                  = build_uri(icTypeUri) 
                scriptCode.append("     icTypeUri                                                    = \'{}\' ".format(icTypeUri)                            )
                scriptCode.append("     map_entry_template.update(permittedInterconnectTypeUri       = icTypeUri)"                                           )

            scriptCode.append("     interconnectMapEntryTemplates.append(map_entry_template)"                                                                )


        
        scriptCode.append("")
        scriptCode.append("     #  Creating SAS logical interconnect group ")
        scriptCode.append("     lig      = oneview_client.sas_logical_interconnect_groups.create(SAS_LOGICAL_INTERCONNECT_GROUP)"                           )
        # New OV resource is created - get its URI to update scope
        # Update scope
        scriptCode.append("     resourceUri  = lig.data[\'uri\']                                  "                                                         )
        if scopesName:
            scriptCode.append("     update_scope({}, resourceUri)                                       " .format(scopesName)                               )

        scriptCode.append("else:"                                                                                                                           )      
        scriptCode.append("     res_name     = res.data[\'name\']                                                "                                          )  
        scriptCode.append("     print \'lig ---> \' + res_name + \' already exists. Skip creating it.....\' "                                               )
    scriptCode.append(CR)
    
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
    build_config(scriptCode, config_file_dest)
    build_function_to_update_scope(scriptCode)


    enclosure_groups = oneview_client.enclosure_groups.get_all()
    #enclosure_groups = oneview_client.enclosure_groups.get_all(sort='name:descending')
    for eg in enclosure_groups:
        _type                               = eg["type"]       
        name                                = eg["name"]
        description                         = eg["description"]  
        ipAddressingMode                    = eg["ipAddressingMode"]
        ipRangeUris                         = eg["ipRangeUris"]                         #[]
        enclosureCount                      = eg["enclosureCount"]
        powerMode                           = eg["powerMode"]

        ambientTemperatureMode              = eg["ambientTemperatureMode"]
        associatedLogicalInterconnectGroups = eg["associatedLogicalInterconnectGroups"] #[]
        interconnectBayMappings             = eg["interconnectBayMappings"]             #[]
        osDeploymentSettings                = eg["osDeploymentSettings"]                # dict

        ### Scopes
        scopesUri                           = eg['scopesUri']
        if scopesUri:
            scopesName                      = get_scope_names(scopesUri, ovIP, headers)

        scriptCode.append(CR)
        scriptCode.append("res          = oneview_client.enclosure_groups.get_by_name(\'{0}\') ".format(name)                                                )
        scriptCode.append("if not res:                                                                    "                                                  ) 
        scriptCode.append("     #===================Attributes for Enclosure Group {} ========================".format(name)                                 )
        scriptCode.append("     print(\'---------Creating Enclosure Group {}\')                               ".format(name)                                 )  

        scriptCode.append("     ENCLOSURE_GROUP                                              = dict()"                                                       )
        scriptCode.append("     ENCLOSURE_GROUP.update(type                                  = \'{}\')".format(_type)                                        )
        scriptCode.append("     ENCLOSURE_GROUP.update(name                                  = \'{}\')".format(name)                                         )
        if description is not None:
            scriptCode.append("     ENCLOSURE_GROUP.update(description                           = \'{}\')".format(description)                              )  
        scriptCode.append("     ENCLOSURE_GROUP.update(enclosureCount                        = {})".format(enclosureCount)                                   )
        scriptCode.append("     ENCLOSURE_GROUP.update(powerMode                             = \'{}\')".format(powerMode)                                    )
        scriptCode.append("     ENCLOSURE_GROUP.update(ambientTemperatureMode                = \'{}\')".format(ambientTemperatureMode)                       )

        ## IP ranges
        scriptCode.append(CR)
        scriptCode.append("     ### IP Ranges region"                                                                                                        ) 
        scriptCode.append("     ENCLOSURE_GROUP.update(ipAddressingMode                      = \'{}\')".format(ipAddressingMode)                             )
        if ipRangeUris is not None:
            scriptCode.append("     ENCLOSURE_GROUP.update(ipRangeUris                           = [])"                                                      )
            for ip_range_uri in ipRangeUris:
                scriptCode.append("     res_pool                                                     = oneview_client.id_pools_ipv4_ranges.get(\'{}\')".format(ip_range_uri) )
                scriptCode.append("     res_pool_name                                                = res[\'name\']"                                        )
                scriptCode.append("     pool_type_ipv4                                               = \'ipv4\'"                                             )
                scriptCode.append("     ipv4_pools                                                   = oneview_client.id_pools.get(pool_type_ipv4)"          )
                scriptCode.append("     for range_uri in ipv4_pools[\'rangeUris\']:"                                                                         )
                scriptCode.append("          this_pool = oneview_client.id_pools_ipv4_ranges.get(range_uri)"                                                 )
                scriptCode.append("          if res_pool_name == this_pool[\'name\']:"                                                                       )
                scriptCode.append("              res_uri = this_pool[\'uri\'] "                                                                              )
                scriptCode.append("              ENCLOSURE_GROUP[\'ipRangeUris\'].append(res_uri)"                                                           )      

        ## Interconnect Bay mappings
        scriptCode.append(CR)
        scriptCode.append("     ### Interconnect Bay mappings region"                                                                                        ) 
        scriptCode.append("     ENCLOSURE_GROUP.update(interconnectBayMappings               = [])"                                                          )
        for ic_bay_mapping in interconnectBayMappings:
            lig_uri             = ic_bay_mapping['logicalInterconnectGroupUri']
            res_uri             = build_uri(lig_uri)
            ic_bay              = ic_bay_mapping['interconnectBay']

            scriptCode.append(""                                                                                                                             )
            scriptCode.append("     bay_mapping                                                  = dict()"                                                   )
            scriptCode.append("     res_uri                                                      = {}".format(build_uri(lig_uri))                            )
            scriptCode.append("     bay_mapping.update(logicalInterconnectGroupUri               = res_uri )"                                                )
            scriptCode.append("     bay_mapping.update(interconnectBay                           = {})".format(ic_bay)                                       )
            if 'enclosureIndex' in ic_bay_mapping: 
                enc_index       = ic_bay_mapping['enclosureIndex']
                scriptCode.append("     bay_mapping.update(enclosureIndex                        = {})".format(enc_index)                                    )
        
            scriptCode.append("     ENCLOSURE_GROUP[\'interconnectBayMappings\'].append(bay_mapping)"                                                        )       
    
        ## OS Deployment Settings
        scriptCode.append(CR)
        scriptCode.append("     ### OS Deployment Settings region"                                                                                           ) 
        scriptCode.append("     ENCLOSURE_GROUP.update(osDeploymentSettings                      = dict())"                                                  )
        scriptCode.append("     ENCLOSURE_GROUP[\'osDeploymentSettings\'].update(deploymentModeSettings  = dict())"                                          )
        deployment_mode        = osDeploymentSettings['deploymentModeSettings']['deploymentMode']
        scriptCode.append("     ENCLOSURE_GROUP[\'osDeploymentSettings\'][\'deploymentModeSettings\'].update(deploymentMode  = \'{}\')".format(deployment_mode))
        deployment_net_uri     = osDeploymentSettings['deploymentModeSettings']['deploymentNetworkUri']
        if deployment_net_uri:
            scriptCode.append("     res_uri                                                      = {}".format(build_uri(deployment_net_uri))                 )
            scriptCode.append("     ENCLOSURE_GROUP[\'osDeploymentSettings\'][\'deploymentModeSettings\'].update(deploymentNetworkUri  = res_uri)"           )


        scriptCode.append("     ENCLOSURE_GROUP[\'osDeploymentSettings\'].update(manageOSDeployment = {})".format(osDeploymentSettings['manageOSDeployment'])) 
                                            
        scriptCode.append(CR)
        scriptCode.append("     #  Creating Enclosure group "                                                                                                )
        scriptCode.append("     eg      = oneview_client.enclosure_groups.create(ENCLOSURE_GROUP)"                                                           )
        # New OV resource is created - get its URI to update scope
        # Update scope
        scriptCode.append("     resourceUri  = eg.data[\'uri\']                                  "                                                           )
        if scopesName:
            scriptCode.append("     update_scope({}, resourceUri)                                       " .format(scopesName)                                )        
        
        scriptCode.append("else:"                                                                                                                            )
        scriptCode.append("     res_name     = res.data[\'name\']                                                "                                           )  
        scriptCode.append("     print \'eg ---> \' + res_name + \' already exists. Skip creating it.....\' "                                                 )
    scriptCode.append(CR)


    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)


# ================================================================================================
#
#   generate_logical_enclosures_script
#
# ================================================================================================
def generate_logical_enclosures_script(to_file):

    scriptCode                  = []
    build_import_files(scriptCode)
    build_constants(scriptCode)
    build_config(scriptCode, config_file_dest)
    build_function_to_update_scope(scriptCode)



    logical_enclosures = oneview_client.logical_enclosures.get_all()

    for le in logical_enclosures:
        _type                                       = le["type"]
        name                                        = le["name"]
        enclosureGroupUri                           = le["enclosureGroupUri"]
        enclosureUris                               = le["enclosureUris"]                         #[]
        fw                                          = le['firmware']
        updateFirmwareOnUnmanagedInterconnect       = fw['updateFirmwareOnUnmanagedInterconnect']
        logicalInterconnectUpdateMode               = fw['logicalInterconnectUpdateMode']
        firmwareBaselineUri                         = fw['firmwareBaselineUri']
        forceInstallFirmware                        = fw["forceInstallFirmware"]
        validateIfLIFirmwareUpdateIsNonDisruptive   = fw['validateIfLIFirmwareUpdateIsNonDisruptive']

        ### Scopes
        scopesUri                                   = le['scopesUri']
        if scopesUri:
            scopesName                              = get_scope_names(scopesUri, ovIP, headers)

        scriptCode.append(CR)
        scriptCode.append("res          = oneview_client.logical_enclosures.get_by_name(\'{0}\') ".format(name)                                              )
        scriptCode.append("if not res:                                                                    "                                                  ) 
        scriptCode.append("     #===================Attributes for Logical Enclosure {} ========================".format(name)                               )
        scriptCode.append("     print(\'---------Creating Logical Enclosure {}\')                               ".format(name)                               )  

        scriptCode.append("     LOGICAL_ENCLOSURE                                            = dict()"                                                       )
        scriptCode.append("     LOGICAL_ENCLOSURE.update(type                                = \'{}\')".format(_type)                                        )
        scriptCode.append("     LOGICAL_ENCLOSURE.update(name                                = \'{}\')".format(name)                                         )
        egUri                                       = build_uri(enclosureGroupUri)
        scriptCode.append("     egUri                                                        = {} ".format(egUri)                                            )
        scriptCode.append("     LOGICAL_ENCLOSURE.update(enclosureGroupUri                   = egUri ) "                                                     )

        scriptCode.append("     LOGICAL_ENCLOSURE.update(enclosureUris                       = [])"                                                          )
        for encUri in enclosureUris:
            scriptCode.append("     encl_uri                                                 = {} ".format(build_uri(encUri))                                )
            scriptCode.append("     LOGICAL_ENCLOSURE[\'enclosureUris'].append(encl_uri)"                                                                    )  

        scriptCode.append("     LOGICAL_ENCLOSURE.update(forceInstallFirmware                = {} )".format(forceInstallFirmware)                            )
        #scriptCode.append("     LOGICAL_ENCLOSURE.update(firmware                            = dict() )"                                                     )
        #scriptCode.append("     LOGICAL_ENCLOSURE['firmware'].update(updateFirmwareOnUnmanagedInterconnect       = {} )".format(updateFirmwareOnUnmanagedInterconnect)  )
        #scriptCode.append("     LOGICAL_ENCLOSURE['firmware'].update(logicalInterconnectUpdateMode               = {} )".format(logicalInterconnectUpdateMode )  )
        #scriptCode.append("     LOGICAL_ENCLOSURE['firmware'].update(firmwareBaselineUri                         = {} )".format(firmwareBaselineUri)  )
        #scriptCode.append("     LOGICAL_ENCLOSURE['firmware'].update(forceInstallFirmware                        = {} )".format(forceInstallFirmware)  )
        #scriptCode.append("     LOGICAL_ENCLOSURE['firmware'].update(validateIfLIFirmwareUpdateIsNonDisruptive   = {} )".format(validateIfLIFirmwareUpdateIsNonDisruptive)  )

        scriptCode.append(CR)
        scriptCode.append("     #  Creating logical enclosure "                                                                                             )
        scriptCode.append("     le      = oneview_client.logical_enclosures.create(LOGICAL_ENCLOSURE)"                                                      )
        # New OV resource is created - get its URI to update scope
        # Update scope
        scriptCode.append("     resourceUri  = le.data[\'uri\']                                    "                                                        )
        if scopesName:
            scriptCode.append("     update_scope({}, resourceUri)                                       " .format(scopesName)                               )

        scriptCode.append("else:"                                                                                                                           )
        scriptCode.append("     res_name     = res.data[\'name\']                                                "                                          )  
        scriptCode.append("     print \'LE ---> \' + res_name + \' already exists. Skip creating it.....\' "                                                )
    scriptCode.append(CR)

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
        connectionSettings                  = prof["connectionSettings"]             # dict
    else:
        connectionSettings                  = prof["connections"]                    # dict

    ### iLO settings
    isLocalAccounts                     = False
    isDirectory                         = False 
    isDirectoryGroups                   = False
    isAdministratorAccount              = False
    managementProcessor                 = prof["managementProcessor"]                # dict
    manageMp                            = managementProcessor["manageMp"]
    if manageMp:
        mpSettings                      = managementProcessor["mpSettings"]          #[]
        for setting in mpSettings:
            args                        = setting['args']                           # dict
            settingType                 = setting['settingType']  
            if 'LocalAccounts' == settingType:
                isLocalAccounts                             = True
                localAccounts                               = []                     #[]
                for account in args['localAccounts']:
                    acc                                     = dict()
                    acc.update(userName                     = account['userName'])
                    acc.update(displayName                  = account['displayName'])
                    acc.update(virtualPowerAndResetPriv     = account['virtualPowerAndResetPriv'])
                    acc.update(remoteConsolePriv            = account['remoteConsolePriv'])
                    acc.update(iLOConfigPriv                = account['iLOConfigPriv'])
                    acc.update(virtualMediaPriv             = account['virtualMediaPriv'])
                    acc.update(userConfigPriv               = account['userConfigPriv'])
                    localAccounts.append(acc)

            if 'DirectoryGroups' == settingType:
                isDirectoryGroups                           = True
                directoryGroupAccounts                      = []                     #[]
                for account in args['directoryGroupAccounts']:
                    acc                                     = dict()
                    acc.update(groupDN                      = account['groupDN'])
                    acc.update(groupSID                     = account['groupSID'])
                    acc.update(remoteConsolePriv            = account['remoteConsolePriv'])
                    acc.update(iLOConfigPriv                = account['iLOConfigPriv'])
                    acc.update(virtualMediaPriv             = account['virtualMediaPriv'])
                    acc.update(userConfigPriv               = account['userConfigPriv'])
                    acc.update(virtualPowerAndResetPriv     = account['virtualPowerAndResetPriv'])
                    directoryGroupAccounts.append(acc)

            if 'Directory' == settingType:
                isDirectory                     = True
                kerberosAuthentication          = args['kerberosAuthentication']
                directoryServerAddress          = args['directoryServerAddress']
                directoryServerPort             = args['directoryServerPort']
                iloObjectDistinguishedName      = args['iloObjectDistinguishedName']
                directoryAuthentication         = args['directoryAuthentication']
                directoryUserContext            = args['directoryUserContext']      #[]


            if 'AdministratorAccount' == settingType:
                isAdministratorAccount          = True
                deleteAdministratorAccount      = args['deleteAdministratorAccount']


    PASSWORD_ACCOUNT                    = 'dummy_password' #  to be updated with real password
    PASSWORD_DIRECTORY                  = 'dummy_password' #  to be updated with real password
    PASSWORD_ADMINISTRATOR              = 'dummy_password' #  to be updated with real password





    #print("#===================Attributes for {0} {1} ========================".format(category,name)                   )

    ###
    scriptCode.append("     PROFILE.update(affinity                      = \'{}\')".format(affinity)                                                         )
    scriptCode.append("     PROFILE.update(wwnType                       = \'{}\')".format(wwnType)                                                          )
    scriptCode.append("     PROFILE.update(macType                       = \'{}\')".format(macType)                                                          )
    scriptCode.append("     PROFILE.update(serialNumberType              = \'{}\')".format(serialNumberType)                                                 )
    scriptCode.append("     PROFILE.update(iscsiInitiatorNameType        = \'{}\')".format(iscsiInitiatorNameType)                                           )
    scriptCode.append("     PROFILE.update(hideUnusedFlexNics            = {})".format(hideUnusedFlexNics)                                                   )
    if serverHardwareTypeUri is not None:
        scriptCode.append("     sht_uri                                      = {}".format(build_uri(serverHardwareTypeUri) )                                 )
        scriptCode.append("     PROFILE.update(serverHardwareTypeUri         = sht_uri)"                                                                     )

    if enclosureGroupUri is not None:
        scriptCode.append("     eg_uri                                       = {}".format(build_uri(enclosureGroupUri))                                      )
        scriptCode.append("     PROFILE.update(enclosureGroupUri             = eg_uri)"                                                                      )


    # Boot and bootMode
    scriptCode.append("     PROFILE.update(boot                          = dict() )"                                                                         )
    scriptCode.append("     PROFILE[\'boot\'].update(manageBoot            = {})".format(boot['manageBoot'])                                                 )
    scriptCode.append("     PROFILE[\'boot\'].update(order                 = [])"                                                                            )
    for boot_entry in boot['order']:
        scriptCode.append("     PROFILE[\'boot\'][\'order\'].append(\'{}\')".format(boot_entry)                                                              )

    scriptCode.append("     PROFILE.update(bootMode                      = dict() )"                                                                         )
    scriptCode.append("     PROFILE[\'bootMode\'].update(manageMode        = {})".format(bootMode['manageMode'])                                             )
    if bootMode['pxeBootPolicy']:
        scriptCode.append("     PROFILE[\'bootMode\'].update(pxeBootPolicy     = \'{}\')".format(bootMode['pxeBootPolicy'])                                  )
    if bootMode['manageMode']:
        scriptCode.append("     PROFILE[\'bootMode\'].update(mode              = \'{}\')".format(bootMode['mode'])                                               )


    # Connection Settings region
    scriptCode.append(CR)
    scriptCode.append("     ##### Connection Settings region               "                                                                                 )
    # Difference between SP and SPT here
    if isTemplate:
        scriptCode.append("     PROFILE.update(connectionSettings            = dict() )"                                                                     )
        scriptCode.append("     PROFILE[\'connectionSettings\'].update(manageConnections = {})".format(connectionSettings['manageConnections'])              )
        scriptCode.append("     PROFILE[\'connectionSettings\'].update(connections = [])"                                                                    )
        connections             =  connectionSettings['connections']  
        scriptCode.append("     connections                                  = PROFILE[\'connectionSettings\']['connections\']"                              )                                                
    else:
       scriptCode.append("     PROFILE.update(connections = [])"                                                                                             ) 
       connections              =  connectionSettings 
       scriptCode.append("      connections                                  = PROFILE['connections\']"                                                       )
    
    if connections:
        for con_element in connections:
            functionType        = con_element['functionType']
            priority            = con_element['boot']['priority']
            con_name            = con_element['name']

            scriptCode.append("     #--------------------- Attributes for connection \'{}\'".format(con_name)                                                )
            scriptCode.append("     connection_element                           = dict() "                                                                  )
            scriptCode.append("     connection_element.update(name               = \'{}\')".format(con_name)                                                 )
            scriptCode.append("     net_uri                                      = {}".format(build_uri(con_element['networkUri'] ) )                        )
            scriptCode.append("     connection_element.update(networkUri         = net_uri)"                                                                 )                
            scriptCode.append("     connection_element.update(portId             = \'{}\')".format(con_element['portId']     )                               )
            scriptCode.append("     connection_element.update(requestedMbps      = \'{}\')".format(con_element['requestedMbps'] )                            )
            scriptCode.append("     connection_element.update(requestedVFs       = \'{}\')".format(con_element['requestedVFs'] )                             )
            scriptCode.append("     connection_element.update(functionType       = \'{}\')".format(functionType )                                            )
            
            ## boot dict
            scriptCode.append("     connection_element.update(boot               = dict() )"                                                                 )
            scriptCode.append("     connection_element[\'boot\'].update(priority   = \'{}\')".format(priority)                                               )
            
            # Difference between SP and SPT here
            if isTemplate:
                if con_element['boot']['bootVlanId']:
                    scriptCode.append("     connection_element[\'boot\'].update(bootVlanId = \'{}\')".format(con_element['boot']['bootVlanId'])              )
            

            # define custom boot type
            if 'NotBootable' not in priority:                                               # Could be PXE , iscsci or SAN
                if 'Ethernet' in functionType:
                    scriptCode.append("     connection_element[\'boot\'].update(ethernetBootType = \'{}\')".format(con_element['boot']['ethernetBootType'])  )   # PXE  
                    # need to work iSCSI boot
                if 'FibreChannel' in functionType:
                    bootVolumeSource    = con_element['boot']['bootVolumeSource']
                    scriptCode.append("     connection_element[\'boot\'].update(bootVolumeSource = \'{}\')".format(bootVolumeSource)                         )   # Managed Volume
                    #if not isTemplate:  # applies to Server profile only
                    #    if 'ManagedVolume' in bootVolumeSource:
                    #        scriptCode.append("     connection_element[\'boot\'].update(targets               = [] )"                            )
                    #        targets         = con_element['boot']['targets']
                    #        for target_element in targets:      # TO BE reviewed as lun and Wwpn depends on the SANstorage section
                    #            scriptCode.append("target                                       = dict()"                                   )
                    #            scriptCode.append("target.update(lun                            = {})".format(target_element['lun'])        )
                    #            scriptCode.append("target.update(arrayWwpn                      = {})".format(target_element['arrayWwpn'])  )
                    #        scriptCode.append("     connection_element['boot']['targets'].append(target)"                                        )                       

            scriptCode.append("     connections.append(connection_element)"                                                                                 )


    
    # local Storage region
    scriptCode.append(CR)
    scriptCode.append("     ##### local Storage region               "                                                                                       )
    scriptCode.append("     PROFILE.update(localStorage                  = dict() )"                                                                         )
    ## Controllers section
    scriptCode.append("     #####    local Storage - Controllers            "                                                                                )
    scriptCode.append("     PROFILE[\'localStorage\'].update(controllers   = [] )"                                                                           )
    for controller in localStorage['controllers']:
        scriptCode.append("     controller                                   = dict()"                                                                       )
        scriptCode.append("     controller.update(deviceSlot                 = \'{}\')".format(controller['deviceSlot'])                                     )
        scriptCode.append("     controller.update(initialize                 = {})".format(controller['initialize'] )                                        )
        scriptCode.append("     controller.update(mode                       = \'{}\')".format(controller['mode'] )                                          )
        # logical Drives
        if controller['logicalDrives'] is not None:
            scriptCode.append("     controller.update(logicalDrives                  = [] )"                                                                 )
            for ld in controller['logicalDrives']:
                scriptCode.append("     ld                                           = dict()"                                                               )
                if ld['name'] is not None:
                    scriptCode.append("     ld.update(name                               = \'{}\')".format(ld['name'])                                       ) 
                scriptCode.append("     ld.update(bootable                           = {})".format(ld['bootable']) 	                                         )
                scriptCode.append("     ld.update(raidLevel                          = \'{}\')".format(ld['raidLevel']) 	                                 ) 
                scriptCode.append("     ld.update(sasLogicalJBODId                   = {})".format(ld['sasLogicalJBODId'])                                   )                    
                if ld['driveTechnology'] is not None:
                    scriptCode.append("     ld.update(driveTechnology                    = \'{}\')".format(ld['driveTechnology'])                            )
                if ld['numPhysicalDrives'] is not None:
                    scriptCode.append("     ld.update(numPhysicalDrives                  = {})".format(ld['numPhysicalDrives'])                              )
                scriptCode.append("     controller[\'logicalDrives\'].append(ld) "                                                                           )
        scriptCode.append("     PROFILE[\'localStorage\'][\'controllers\'].append(controller)"                                                               )

    ## sas Logical JBODs region
    scriptCode.append("     #####    local Storage -  sas Logical JBODs            "                                                                         )
    scriptCode.append("     PROFILE[\'localStorage\'].update(sasLogicalJBODs = [] )"                                                                         )
    for jbod in localStorage['sasLogicalJBODs']:
        scriptCode.append("     jbod                                         = dict()"                                                                       )
        scriptCode.append("     jbod.update(name                             = \'{}\')".format(jbod['name'])                                                 )
        scriptCode.append("     jbod.update(deviceSlot                       = \'{}\')".format(jbod['deviceSlot'])                                           )
        scriptCode.append("     jbod.update(driveTechnology                  = \'{}\')".format(jbod['driveTechnology'])                                      )

        scriptCode.append("     jbod.update(driveMinSizeGB                   = {})".format(jbod['driveMinSizeGB'])                                           )
        scriptCode.append("     jbod.update(driveMaxSizeGB                   = {})".format(jbod['driveMaxSizeGB'])                                           )
        scriptCode.append("     jbod.update(numPhysicalDrives                = {})".format(jbod['numPhysicalDrives'])                                        )
        scriptCode.append("     jbod.update(id                               = {})".format(jbod['id'])                                                       )
        scriptCode.append("     PROFILE[\'localStorage\'][\'sasLogicalJBODs\'].append(jbod)"                                                                 )


    # Firmware
    scriptCode.append(CR)
    scriptCode.append("     ##### Firmware region               "                                                                                            )
    scriptCode.append("     PROFILE.update(firmware                      = dict() )"                                                                         )
    scriptCode.append("     PROFILE[\'firmware\'].update(manageFirmware    = {})".format(firmware['manageFirmware'])                                         )
    scriptCode.append("     PROFILE[\'firmware\'].update(forceInstallFirmware = {})".format(firmware['forceInstallFirmware'])                                )
    if firmware['manageFirmware']:
        scriptCode.append("     PROFILE[\'firmware\'].update(firmwareInstallType = \'{}\')".format(firmware['firmwareInstallType'] )                         )
        scriptCode.append("     PROFILE[\'firmware\'].update(firmwareActivationType = \'{}\')".format(firmware['firmwareActivationType'])                    )
        scriptCode.append("     PROFILE[\'firmware\'].update(firmwareBaselineUri = \'{}\')".format(firmware['firmwareBaselineUri'])                          )   


    # BIOS 
    manageBios                            = bios['manageBios']
    scriptCode.append(CR)
    scriptCode.append("     ##### BIOS settings region               "                                                                                       )
    scriptCode.append("     PROFILE.update(bios                          = dict() )"                                                                         )
    scriptCode.append("     PROFILE[\'bios\'].update(manageBios            = {}) ".format(manageBios)                                                        )
    scriptCode.append("     PROFILE[\'bios\'].update(overriddenSettings    = []) "                                                                           )
    if manageBios:
        for setting in bios['overriddenSettings']:
            scriptCode.append("     setting                                      = dict() "                                                                  )   
            scriptCode.append("     setting.update(id                            = \'{}\')".format(setting['id'])                                            ) 
            scriptCode.append("     setting.update(value                         = \'{}\')".format(setting['value'])                                         ) 
            scriptCode.append("     PROFILE[\'bios\'][\'overriddenSettings\'].append(setting)"                                                               ) 

    # iLO settings region
    if manageMp:
        scriptCode.append(CR)
        scriptCode.append("     ##### ILO settings region                                                 "                                                  )
        scriptCode.append("     PROFILE.update(managementProcessor                         = dict()      )"                                                  )
        scriptCode.append("     PROFILE['managementProcessor'].update(manageMp             = {}          )".format(manageMp)                                 )
        scriptCode.append("     PROFILE[\'managementProcessor\'].update(mpSettings         = []          )"                                                  )


        if isLocalAccounts:
            scriptCode.append("     setting_element                                            = dict()      "                                               )
            scriptCode.append("     setting_element.update(args                                = dict()      )"                                              )
            scriptCode.append("     setting_element.update(settingType                     = \'LocalAccounts\'      )"                                       )
            scriptCode.append("     setting_element[\'args\'].update(localAccounts         = []          )"                                                  )
            for account in localAccounts:
                scriptCode.append("     account                                               = dict()   "                                                   )
                scriptCode.append("     account.update(userName                               = \'{}\'  )".format(account['userName'])                       ) 
                scriptCode.append("     account.update(displayName                            = \'{}\'  )".format(account['displayName'])                    ) 
                scriptCode.append("     account.update(virtualPowerAndResetPriv               = {}      )".format(account['virtualPowerAndResetPriv'])       ) 
                scriptCode.append("     account.update(remoteConsolePriv                      = {}      )".format(account['remoteConsolePriv'])              ) 
                scriptCode.append("     account.update(iLOConfigPriv                          = {}      )".format(account['iLOConfigPriv'])                  ) 
                scriptCode.append("     account.update(virtualMediaPriv                       = {}      )".format(account['virtualMediaPriv'])               ) 
                scriptCode.append("     account.update(userConfigPriv                         = {}      )".format(account['userConfigPriv'])                 ) 
                scriptCode.append("     account.update(password                               = \'{}\'  )".format(PASSWORD_ACCOUNT)                          ) 

                scriptCode.append("     setting_element[\'args\'][\'localAccounts\'].append(account)     "                                                   )
            
            scriptCode.append("     PROFILE[\'managementProcessor\'][\'mpSettings\'].append(setting_element)"                                               )
            isLocalAccounts     = False


        if isDirectoryGroups:
            scriptCode.append("     setting_element                                            = dict()      "                                               )
            scriptCode.append("     setting_element.update(args                                = dict()      )"                                              )
            scriptCode.append("     setting_element.update(settingType                         = \'DirectoryGroups\'      )"                                 )
            scriptCode.append("     setting_element[\'args\'].update(directoryGroupAccounts    = []          )"                                              )
            for account in directoryGroupAccounts:
                scriptCode.append("     account                                               = dict()   "                                                   )
                scriptCode.append("     account.update(groupSID                               = \'{}\'  )".format(account['groupSID'])                       ) 
                scriptCode.append("     account.update(groupDN                                = \'{}\'  )".format(account['groupDN'])                        ) 
                scriptCode.append("     account.update(virtualPowerAndResetPriv               = {}      )".format(account['virtualPowerAndResetPriv'])       ) 
                scriptCode.append("     account.update(remoteConsolePriv                      = {}      )".format(account['remoteConsolePriv'])              ) 
                scriptCode.append("     account.update(iLOConfigPriv                          = {}      )".format(account['iLOConfigPriv'])                  ) 
                scriptCode.append("     account.update(virtualMediaPriv                       = {}      )".format(account['virtualMediaPriv'])               ) 
                scriptCode.append("     account.update(userConfigPriv                         = {}      )".format(account['userConfigPriv'])                 ) 

                scriptCode.append("     setting_element[\'args\'][\'directoryGroupAccounts\'].append(account)     "                                          )
            
            scriptCode.append("     PROFILE[\'managementProcessor\'][\'mpSettings\'].append(setting_element)"                                               )
            isDirectoryGroups     = False

        if isAdministratorAccount:
            scriptCode.append("     setting_element                                            = dict()      "                                              )
            scriptCode.append("     setting_element.update(args                                = dict()      )"                                             )
            scriptCode.append("     setting_element.update(settingType                        = \'AdministratorAccount\'      )"                            )
            scriptCode.append("     setting_element[\'args\'].update(deleteAdministratorAccount = {}        )".format(deleteAdministratorAccount)           )
            scriptCode.append("     setting_element[\'args\'].update(password                 = \'{}\'      )".format(PASSWORD_ADMINISTRATOR)               )
            scriptCode.append("     PROFILE[\'managementProcessor\'][\'mpSettings\'].append(setting_element)"                                               )
            isAdministratorAccount         = False


        if isDirectory:
            scriptCode.append("     setting_element                                            = dict()      "                                              )
            scriptCode.append("     setting_element.update(args                                = dict()      )"                                             )
            scriptCode.append("     setting_element.update(settingType                        = \'Directory\'      )"                                       )
            scriptCode.append("     setting_element[\'args\'].update(kerberosAuthentication   = {}          )".format(kerberosAuthentication)               ) 
            scriptCode.append("     setting_element[\'args\'].update(directoryServerAddress   = \'{}\'      )".format(directoryServerAddress)               )
            scriptCode.append("     setting_element[\'args\'].update(directoryServerPort      = {}          )".format(directoryServerPort)                  )
            scriptCode.append("     setting_element[\'args\'].update(iloObjectDistinguishedName = \'{}\'    )".format(iloObjectDistinguishedName)           )
            scriptCode.append("     setting_element[\'args\'].update(directoryAuthentication  = \'{}\'      )".format(directoryAuthentication)              )
            scriptCode.append("     setting_element[\'args\'].update(password                 = \'{}\'      )".format(PASSWORD_DIRECTORY)                   )
            # TBD
            scriptCode.append("     setting_element[\'args\'].update(directoryUserContext     = []      )"                                                  )
            scriptCode.append("     PROFILE[\'managementProcessor\'][\'mpSettings\'].append(setting_element)"                                               )
            isDirectory         = False

            

    # OS Deployment Settings
    scriptCode.append(CR)
    scriptCode.append("     ##### OS Deployment settings region               "                                                                              )
    scriptCode.append("     PROFILE.update(osDeploymentSettings          = dict() )"                                                                         )
    if osDeploymentSettings:
        scriptCode.append("     try:"                                                                                                                        )
        scriptCode.append("         deployment_plan_uri = \'{}\'".format(osDeploymentSettings['osDeploymentPlanUri'])                                        )
        scriptCode.append("         res_uri = oneview_client.os_deployment_plans.get(deployment_plan_uri)"                                                   )
        scriptCode.append("     except HPOneViewException as error:"                                                                                         )
        scriptCode.append("         res_uri = \'\'   # OS Deployment plan not found"                                                                         )
        scriptCode.append("     if res_uri:"                                                                                                                 )
        scriptCode.append("          PROFILE[\'osDeploymentSettings\'].update(osDeploymentPlanUri = \'res_uri\')"                                            )
        scriptCode.append("          PROFILE[\'osDeploymentSettings\'].update(osCustomAttributes = [] )"                                                     )
        for setting in osDeploymentSettings['osCustomAttributes']:
            scriptCode.append("          setting                                      = dict() "                                                             )   
            scriptCode.append("          setting.update(name                          = \'{}\')".format(setting['name'])                                     ) 
            scriptCode.append("          setting.update(value                         = \'{}\')".format(setting['value'])                                    ) 

            scriptCode.append("          PROFILE[\'osDeploymentSettings\'][\'osCustomAttributes\'].append(setting)"                                          ) 

    # San Storage region
    manageSanStorage        = sanStorage['manageSanStorage']
    scriptCode.append(CR)
    scriptCode.append("     ##### San Storage region               "                                                                                         )
    scriptCode.append("     PROFILE.update(sanStorage                    = dict() )"                                                                         )
    scriptCode.append("     PROFILE[\'sanStorage\'].update(volumeAttachments = [] )"                                                                         )
    scriptCode.append("     PROFILE[\'sanStorage\'].update(manageSanStorage  = \'{}\' )".format(manageSanStorage)                                            )

    if manageSanStorage:
        scriptCode.append("     PROFILE[\'sanStorage\'].update(hostOSType      = \'{}\')".format(sanStorage['hostOSType'])                                   )
        scriptCode.append("     PROFILE[\'sanStorage\'][\'volumeAttachments\'] = dict() )"                                                                   )
        scriptCode.append("     volumeAttachments                            = PROFILE[\'sanStorage\'][\'volumeAttachments\']  )"                            )

        volumeAttachments           = sanStorage['volumeAttachments']
        for volume in volumeAttachments:
            lunType                 = volume['lunType']         
            scriptCode.append("     volume                                       = dict()"                                                                   )
            scriptCode.append("     volume.update(lunType                        = \'{}\')".format(lunType)                                                  )
            scriptCode.append("     volume.update(isBootVolume                   = {}    )".format(volume['isBootVolume'])                                   )    
            scriptCode.append("     volume.update(id                             = {}    )".format(volume['id'])                                             )
            scriptCode.append("     volume.update(lun                            = {}    )".format(volume['lun'])                                            )

            volumeStoragePoolUri    = volume['volumeStoragePoolUri']
            volumeUri               = volume['volumeUri']
            volumeStorageSystemUri  = volume['volumeStorageSystemUri']
            scriptCode.append("     volume.update(volumeStorageSystemUri                     = {}    )".format(build_uri(volumeStorageSystemUri))            )
            if volumeUri:
                scriptCode.append("     volume.update(volumeUri                                  = {}    )".format(build_uri(volumeUri))                     )
            
            # find on storage pools
            storage_pools           = oneview_client.storage_pools.get_all(filter='isManaged=True')
            for pool in storage_pools:
                pool_name = ''
                if  volumeStoragePoolUri == pool['uri']:
                    pool_name = pool['name']
            if pool_name:
                scriptCode.append("             pool_name = \'{}\'".format(pool_name)                                                                        )
                scriptCode.append("             storage_pools  = oneview_client.storage_pools.get_all(filter=\'isManaged=True\')"                            )
                scriptCode.append("             for pool in storage_pools:"                                                                                  )
                scriptCode.append("                 if pool_name == pool[\'name\']:"                                                                         )
                scriptCode.append("                      volume.update(volumeStoragePoolUri   = pool[\'uri\']"                                               )
         
                      
            
            
            #if 'Manual' in lunType:

            scriptCode.append("     volumeAttachments.append(volume)"                                                                                        )            

    
    
    
    scriptCode.append(CR)
    scriptCode.append("     #  Creating {0} ---> {1} ".format(category,name)                                                                                 )
    if 'server-profile-templates' in category:
        scriptCode.append("     spt      = oneview_client.server_profile_templates.create(PROFILE)"                                                          )                 
    else:
        scriptCode.append("     sp      = oneview_client.server_profiles.create(PROFILE)"                                                                    ) 


                                                                                 
# ================================================================================================
#
#   generate_server_profile_templates_script
#
# ================================================================================================
def generate_server_profile_templates_script(to_file):
    
    scriptCode                  = []
    build_import_files(scriptCode)
    build_constants(scriptCode)
    build_function_to_update_scope(scriptCode)
    build_config(scriptCode, config_file_dest)


    
    server_profile_templates = oneview_client.server_profile_templates.get_all()


    for prof in server_profile_templates:
        category                            = prof["category"]
        _type                               = prof["type"]
        name                                = prof["name"]  
        serverProfileDescription            = prof["serverProfileDescription"]
        
        #### Scopes
        scopesUri                           = prof['scopesUri']
        if scopesUri:
            scopesName                      = get_scope_names(scopesUri, ovIP, headers)

        scriptCode.append(CR)
        scriptCode.append("res          = oneview_client.server_profile_templates.get_by_name(\'{0}\') ".format(name)                                        )
        scriptCode.append("if not res:                                                                    "                                                  )  
        scriptCode.append("     print(\'---------Creating server profile template {}\')            ".format(name)                                            )  
        scriptCode.append("     #===================Attributes for {0} {1} ========================".format(category,name)                                   )
        scriptCode.append("     PROFILE                                      = dict()"                                                                       )
        scriptCode.append("     PROFILE.update(type                          = \'{}\')".format(_type)                                                        )
        scriptCode.append("     PROFILE.update(name                          = \'{}\')".format(name)                                                         )

        generate_profile_or_templates_script(scriptCode, prof )
        # New OV resource is created - get its URI to update scope from spt
        # Update scope
        scriptCode.append("     resourceUri  = spt.data[\'uri\']                                  "                                                         )
        if scopesName:
            scriptCode.append("     update_scope({}, resourceUri)                                       " .format(scopesName)                                )

        scriptCode.append("else:"                                                                                                                            )
        scriptCode.append("     res_name     = res.data[\'name\']                                                "                                           )  
        scriptCode.append("     print \'SPT ---> \' + res_name + \' already exists. Skip creating it.....\' "                                                )
    scriptCode.append(CR)

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
    build_function_to_update_scope(scriptCode)
    build_config(scriptCode, config_file_dest)


    server_profiles                         = oneview_client.server_profiles.get_all()

    for prof in server_profiles:
        category                            = prof["category"]
        _type                               = prof["type"]
        name                                = prof["name"]
        serverHardwareUri                   = prof["serverHardwareUri"]
        serverProfileTemplateUri            = prof["serverProfileTemplateUri"]

    
        scriptCode.append(CR)
        scriptCode.append("res          = oneview_client.server_profiles.get_by_name(\'{0}\') ".format(name)                                                  )
        scriptCode.append("if not res:                                                                    "                                                   )  
        scriptCode.append("     print(\'---------Creating server profile {}\')                     ".format(name)                                             )  
        scriptCode.append("     #===================Attributes for {0} {1} ========================".format(category,name)                                    )

        # POWER OFF server
        scriptCode.append("     print \'Powering off server     {}\'.format(this_server.data[\'name\'])"                                                      )
        scriptCode.append("     SERVER_STATE_OFF                             = dict()"                                                                        )
        scriptCode.append("     SERVER_STATE_OFF.update(powerState           = \'Off\')          "                                                            )
        scriptCode.append("     server_power                                 = this_server.update_power_state(SERVER_STATE_OFF) "                             )

        scriptCode.append("     PROFILE                                      = dict()"                                                                        )
        scriptCode.append("     PROFILE.update(type                          = \'{}\')".format(_type)                                                         )
        scriptCode.append("     PROFILE.update(name                          = \'{}\')".format(name)                                                          )

        ### Scopes
        scopesUri                           = prof['scopesUri']
        if scopesUri:
            scopesName                      = get_scope_names(scopesUri, ovIP, headers)
        
        ### Server Hardware
        if serverHardwareUri:
            scriptCode.append("     s_uri                                        = {}".format(build_uri(serverHardwareUri) )                                  )
            scriptCode.append("     PROFILE.update(serverHardwareUri             = s_uri)"                                                                    )  
            scriptCode.append("     this_server                                  = oneview_client.server_hardware.get_by_uri(s_uri)"                          )   



        ### Server profile Template
        if serverProfileTemplateUri:
            scriptCode.append("     spt_uri                                      = {}".format(build_uri(serverProfileTemplateUri) )                           )
            scriptCode.append("     PROFILE.update(serverProfileTemplateUri      = spt_uri)"                                                                  )    
            

            # Structure attributes
            scriptCode.append("     this_spt                                     = oneview_client.server_profile_templates.get_by_uri(spt_uri)"               )       
            scriptCode.append("     PROFILE.update(firmware                      = copy.deepcopy(this_spt.data[\'firmware\']))"                               )
            scriptCode.append("     PROFILE.update(boot                          = copy.deepcopy(this_spt.data[\'boot\']))"                                   )
            scriptCode.append("     PROFILE.update(bootMode                      = copy.deepcopy(this_spt.data[\'bootMode\']))"                               )
            scriptCode.append("     PROFILE.update(bios                          = copy.deepcopy(this_spt.data[\'bios\']))"                                   )
            scriptCode.append("     PROFILE.update(localStorage                  = copy.deepcopy(this_spt.data[\'localStorage\']))"                           )
            scriptCode.append("     PROFILE.update(sanStorage                    = copy.deepcopy(this_spt.data[\'sanStorage\']))"                             )
            scriptCode.append("     PROFILE.update(osDeploymentSettings          = copy.deepcopy(this_spt.data[\'osDeploymentSettings\']))"                   )
            scriptCode.append("     PROFILE.update(connectionSettings            = copy.deepcopy(this_spt.data[\'connectionSettings\']))"    )
            # Remove manageConnectionsattribute coming from template
            scriptCode.append("     del PROFILE[\'connectionSettings\'][\'manageConnections\']"                                                               )

            # Single value attribute
            scriptCode.append("     PROFILE.update(description                   = copy.copy(this_spt.data[\'description\']))"                                )
            scriptCode.append("     PROFILE.update(affinity                      = copy.copy(this_spt.data[\'affinity\']))"                                   )
            scriptCode.append("     PROFILE.update(wwnType                       = copy.copy(this_spt.data[\'wwnType\']))"                                    )
            scriptCode.append("     PROFILE.update(macType                       = copy.copy(this_spt.data[\'macType\']))"                                    )
            scriptCode.append("     PROFILE.update(serialNumberType              = copy.copy(this_spt.data[\'serialNumberType\']))"                           )
            scriptCode.append("     PROFILE.update(iscsiInitiatorNameType        = copy.copy(this_spt.data[\'iscsiInitiatorNameType\']))"                     )
            scriptCode.append("     PROFILE.update(hideUnusedFlexNics            = copy.copy(this_spt.data[\'hideUnusedFlexNics\']))"                         )

            # Create profile
            scriptCode.append("     print \'Creating server profile {}\'.format(this_server.data[\'name\'])"                                                 )
            scriptCode.append("     sp                                           = oneview_client.server_profiles.create(PROFILE)"                           )
               
        else:   # Server profile created manually
            generate_profile_or_templates_script(scriptCode, prof)

        # New OV resource is created - get its URI to update scope
        # Update scope
        scriptCode.append("     resourceUri  = sp.data[\'uri\']                                  "                                                         )
        if scopesName:
            scriptCode.append("     update_scope({}, resourceUri)                                       " .format(scopesName)                                )

        scriptCode.append("else:"                                                                                                                            )
        scriptCode.append("     res_name     = res.data[\'name\']                                                "                                           ) 
        scriptCode.append("     print \'SP ---> \' + res_name + \' already exists. Skip creating it.....\' "                                                 )
    scriptCode.append(CR)


    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)


# ############################################################################################################
#
#                       OneView Settings
#
# ############################################################################################################


# ================================================================================================
#
#   generate_id_pools_ipv4_subnets_script
#
# ================================================================================================
def generate_id_pools_ipv4_subnets_script(to_file):
    
    scriptCode                              = []
    build_import_files(scriptCode)
    build_constants(scriptCode)
    build_config(scriptCode, config_file_dest)

    all_subnets =  oneview_client.id_pools_ipv4_subnets.get_all()
    for subnet in all_subnets:
        _type                   = subnet['type']
        networkId               = subnet['networkId']
        subnetmask              = subnet['subnetmask']
        gateway                 = subnet['gateway']
        domain                  = subnet['domain']
        dnsServers              = subnet['dnsServers'] # []

        scriptCode.append(CR)
        scriptCode.append("#===================Attributes for subnet {} ========================".format(networkId)                                     )

        scriptCode.append("isExisted 	                                    = False"                                                                    )
        scriptCode.append("all_subnets                                      = oneview_client.id_pools_ipv4_subnets.get_all()"                           )
        scriptCode.append("for subnet in all_subnets:                                 "                                                                 )
        scriptCode.append("     if \'{}\' in subnet[\'networkId\']:                   ".format(networkId)                                               )
        scriptCode.append("         isExisted 	                             = True   "                                                                 )
        scriptCode.append("         break                                             "                                                                 )
        scriptCode.append("if not isExisted:                                          "                                                                 )
        scriptCode.append("     SUBNET                                       = dict() "                                                                 )
        scriptCode.append("     SUBNET.update(type                           = \'{}\')".format(_type)                                                   )
        scriptCode.append("     SUBNET.update(networkId                      = \'{}\')".format(networkId)                                               )
        scriptCode.append("     SUBNET.update(subnetmask                     = \'{}\')".format(subnetmask)                                              )
        scriptCode.append("     SUBNET.update(gateway                        = \'{}\')".format(gateway)                                                 )
        scriptCode.append("     SUBNET.update(domain                         = \'{}\')".format(domain)                                                  )
        scriptCode.append("     SUBNET.update(dnsServers                     = [])    "                                                                 )

        for dns in dnsServers:
            scriptCode.append("     SUBNET[\'dnsServers\'].append(\'{}\')".format(dns)                                                                  )
        
        scriptCode.append(CR)
        scriptCode.append("     #  Creating subnet {} ".format(networkId)                                                                               )
        scriptCode.append("     print \'Creating subnet {} \'               ".format(networkId)                                                         )
        scriptCode.append("     SUBNET      = oneview_client.id_pools_ipv4_subnets.create(SUBNET)"                                                      ) 
        scriptCode.append("else:                                                                 "                                                      )
        scriptCode.append("     print \'subnet {} already existed. Skip creating it... \' ".format(networkId)                                           )


    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)



# ================================================================================================
#
#   generate_ranges_script helper function
#
# ================================================================================================

def generate_ranges_script(pool_type,function,to_file):

    scriptCode                              = []
    build_import_files(scriptCode)
    build_constants(scriptCode)
    build_config(scriptCode, config_file_dest)

    pool                        = oneview_client.id_pools.get(pool_type)
    if pool:
        name                    = pool['name']
        rangeUris               = pool['rangeUris']         # []
        for range_uri  in rangeUris:
            range               = function.get(range_uri)
            _type               = range['type']
            rangeCategory       = range['rangeCategory']
            name                = range['name']
            startAddress        = range['startAddress']
            endAddress          = range['endAddress'] 
            enabled             = range['enabled']

            scriptCode.append(CR)
            scriptCode.append("isExisted                                    = False                 "                                                   ) 
            scriptCode.append("pool_type                                    = \'{}\'".format(pool_type)                                                 )
            scriptCode.append("pool                                         = oneview_client.id_pools.get(pool_type)"                                   )
            scriptCode.append("if pool:                                                             "                                                   )
            scriptCode.append("     rangeUris                               = pool[\'rangeUris\']   "                                                   )
            scriptCode.append("     for range_uri  in rangeUris:                                    "                                                   )
            scriptCode.append("         range                               = oneview_client.id_pools_{}_ranges.get(range_uri) ".format(pool_type)      )
            scriptCode.append("         name                                = range[\'name\']       "                                                   )
            scriptCode.append("         startAddress                        = range[\'startAddress\']"                                                  )
            scriptCode.append("         endAddress                          = range[\'endAddress\'] "                                                   )
            scriptCode.append("         if name == \'{0}\' and startAddress == \'{1}\' and endAddress == \'{2}\':".format(name,startAddress,endAddress) )
            scriptCode.append("             isExisted                       = True                  "                                                   )   
            scriptCode.append("             break                                                   "                                                   ) 

            scriptCode.append("if not isExisted:                                                    "                                                   ) 
            scriptCode.append("     #===================Attributes for id pools  {0} {1} ========================".format(pool_type,name)               )

            scriptCode.append("     RANGE                                       = dict() "                                                              )
            scriptCode.append("     RANGE.update(type                           = \'{}\')".format(_type)                                                )
            scriptCode.append("     RANGE.update(name                           = \'{}\')".format(name)                                                 )
            scriptCode.append("     RANGE.update(enabled                        = {})    ".format(enabled)                                              )
            scriptCode.append("     RANGE.update(startAddress                   = \'{}\')".format(startAddress)                                         )
            scriptCode.append("     RANGE.update(endAddress                     = \'{}\')".format(endAddress)                                           )
                        
            #subnetUri
            if 'ipv4' in pool_type:
                subnetUri           = range['subnetUri']
                if subnetUri:
                    networkId       = oneview_client.id_pools_ipv4_subnets.get(subnetUri)['networkId']
                    scriptCode.append("     all_subnets                         = oneview_client.id_pools_ipv4_subnets.get_all()"                      )
                    scriptCode.append("     for subnet in all_subnets:                       "                                                         )
                    scriptCode.append("         if \'{}\' in subnet[\'networkId\']:             ".format(networkId)                                    )
                    scriptCode.append("             subnetUri                  = subnet[\'uri\'] "                                                     )
                    scriptCode.append("             break                                   "                                                          )                                                             
                    scriptCode.append("     RANGE.update(subnetUri              = subnetUri )"                                                         )
            else:
                scriptCode.append("     RANGE.update(rangeCategory                  = \'{}\')".format(rangeCategory)                                   )
            scriptCode.append(CR)
            scriptCode.append("     #  Creating id pools {0} ---> {1}    ".format(pool_type, name)                                                     )
            scriptCode.append("     print \' Creating id pools {0} start --> {1} end --> {2}\'  ".format(pool_type, startAddress, endAddress)          )
            scriptCode.append("     range      = oneview_client.id_pools_{}_ranges.create(RANGE)".format(pool_type)                                    ) 
            scriptCode.append("else:                                                            "                                                      ) 
            scriptCode.append("     print \'id pool name ---> {0} start --> {1} end --> {2} already existed. Skip creating it...\' ".format(pool_type, startAddress, endAddress)  )                                                                                                    

    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)

# ================================================================================================
#
#   generate_id_pools_ipv4_ranges_script
#
# ================================================================================================
def generate_id_pools_ipv4_ranges_script(to_file):

    generate_ranges_script('ipv4',oneview_client.id_pools_ipv4_ranges, to_file)    


# ================================================================================================
#
#   generate_id_pools_vsn_ranges_script
#
# ================================================================================================
def generate_id_pools_vsn_ranges_script(to_file):

    generate_ranges_script('vsn',oneview_client.id_pools_vsn_ranges, to_file)


# ================================================================================================
#
#   generate_id_pools_vmac_ranges_script
#
# ================================================================================================
def generate_id_pools_vmac_ranges_script(to_file):

    generate_ranges_script('vmac',oneview_client.id_pools_vmac_ranges, to_file)


# ================================================================================================
#
#   generate_id_pools_vwwn_ranges_script
#
# ================================================================================================
def generate_id_pools_vwwn_ranges_script(to_file):

    generate_ranges_script('vwwn',oneview_client.id_pools_vwwn_ranges, to_file)


# ================================================================================================
#
#   generate_appliance_time_and_locale_configuration_script
#
# ================================================================================================
def generate_appliance_time_and_locale_configuration_script(to_file):
    
    scriptCode                              = []
    build_import_files(scriptCode)
    build_constants(scriptCode)
    build_config(scriptCode, config_file_dest)

    time_and_locale = oneview_client.appliance_time_and_locale_configuration.get()

    scriptCode.append(CR)
    scriptCode.append("#===================Attributes for date time   ========================"                                                       )

    scriptCode.append("DATETIME                                    = dict()"                                                                          )
    scriptCode.append("DATETIME.update(locale                      = \'{}\')".format(time_and_locale['locale'])                                       )
    scriptCode.append("DATETIME.update(ntpServers                  = [])"                                                                             )
    for ntp in time_and_locale['ntpServers']:
        scriptCode.append("DATETIME[\'ntpServers\'].append(\'{}\')".format(ntp)                                                                       )

    scriptCode.append(CR)
    scriptCode.append("#  upodating date time "                                                                                                       )
    scriptCode.append("time_and_locale = oneview_client.appliance_time_and_locale_configuration.update(DATETIME)"                                     ) 


    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)    


# ================================================================================================
#
#   generate_scopes_script
#
# ================================================================================================
def generate_scopes_script(to_file):
    
    scriptCode                              = []
    build_import_files(scriptCode)
    build_constants(scriptCode)
    build_config(scriptCode, config_file_dest)

    all_scopes = oneview_client.scopes.get_all()
    for scope in all_scopes:
        _type                   = scope['type']
        name                    = scope['name']
        description             = scope['description']

        scriptCode.append(CR)
        scriptCode.append("scope                    = oneview_client.scopes.get_by_name(\'{}\')     ".format(name)                                      )
        scriptCode.append("isExisted                = True if scope else False                      "                                                   )
        scriptCode.append("if not isExisted:                                                        "                                                   )
        scriptCode.append("     #===================Attributes for scope  ========================  "                                                   )
        scriptCode.append("     print \'------ Creating scope {} \'                  ".format(name)                                                     )
        scriptCode.append("     SCOPE                                    = dict()    "                                                                  )
        scriptCode.append("     SCOPE.update(type                        = \'{}\')   ".format(_type)                                                    )
        scriptCode.append("     SCOPE.update(name                        = \'{}\')   ".format(name)                                                     )
        if description:
            scriptCode.append("     SCOPE.update(description                 = \'{}\')   ".format(description)                                          )
        scriptCode.append("     sc                                       = oneview_client.scopes.create(SCOPE) "                                        )

        scriptCode.append("else:                                                                    "                                                   )
        scriptCode.append("     print \'Scope {} already existed. Skip creating it....\'            ".format(name)                                      )


    scriptCode.append(CR)
    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)




# ############################################################################################################
#
#                   Main Entry point
#
# ############################################################################################################


if __name__ == "__main__":

    if len(sys.argv) >= 3:
        config_file_src     = sys.argv[1]
        config_file_dest    = sys.argv[2]
    else:
        print "No oneview_config.json for OV source and OV destination are provided. Please run the script as \' python convertto_pyscripts.py oneview_config_src.json oneview_config_dest.json\'  "
        exit()

# MAIN
#===================Connect to OneView ========================
print(CR)
print '#===================Connect to OneView ========================'
print(CR)

with open(config_file_src) as json_data:
    config = json.load(json_data)
oneview_client = OneViewClient(config)

ovIP                          = config['ip']
ovAPI                         = config['api_version']
ovUser                        = config['credentials']['userName']
ovPassword                    = config['credentials']['password']
cred                          = dict() 
cred.update(userName          = '{}'.format(ovUser) )
cred.update(password          = '{}'.format(ovPassword) )
auth_uri                      = 'https://{}/rest/login-sessions'.format(ovIP)
headers                       = { 
    'content-type': 'application/json',
    'X-Api-Version': '{}'  .format(ovAPI)
}                                
resp = requests.post(auth_uri, headers=headers, timeout=60, verify=False,data=json.dumps(cred))
token                         = json.loads(resp.text) 
sessionID                     = token['sessionID'] 
headers.update(Auth           = '{}' .format(sessionID) )


# =================================== OV Settings =========================================================

#--- subnets
to_file         = "ov_id_pools_ipv4_subnets.py"
print(CR)
print("Generating python script file ====>      {}".format(to_file)                 )
generate_id_pools_ipv4_subnets_script(to_file)

#--- ipv4 pool ranges
to_file         = "ov_id_pools_ipv4_ranges.py"
print(CR)
print("Generating python script file ====>      {}".format(to_file)                 )
generate_id_pools_ipv4_ranges_script(to_file)

#--- vMAC pool ranges
to_file         = "ov_id_pools_vmac_ranges.py"
print(CR)
print("Generating python script file ====>      {}".format(to_file)                 )
generate_id_pools_vmac_ranges_script(to_file)

#--- vwwn pool ranges
to_file         = "ov_id_pools_vwwn_ranges.py"
print(CR)
print("Generating python script file ====>      {}".format(to_file)                 )
generate_id_pools_vwwn_ranges_script(to_file)

#--- vsn pool ranges
to_file         = "ov_id_pools_vsn_ranges.py"
print(CR)
print("Generating python script file ====>      {}".format(to_file)                 )
generate_id_pools_vsn_ranges_script(to_file)

#--- Date Time
to_file         = "ov_time_and_locale.py"
print(CR)
print("Generating python script file ====>      {}".format(to_file)                 )
generate_appliance_time_and_locale_configuration_script(to_file)

#--- Scopes
to_file         = "ov_scopes.py"
print(CR)
print("Generating python script file ====>      {}".format(to_file)                 )
generate_scopes_script(to_file)

# =================================== OV Resources =========================================================

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

#--- logical enclosures
to_file         = "ov_logical_enclosures.py"
print(CR)
print("Generating python script file ====>      {}".format(to_file)                 )
generate_logical_enclosures_script(to_file)

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


