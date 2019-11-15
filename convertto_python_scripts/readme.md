# Generate python scripts from OneView

convertto_pyscripts.py is a python script that generates python code to configure new OneView instances. The script queries an existing OV instance (called 'Master') and based on resources and attributes configured in this instance, it will create scripts that call OV python SDK. Those scripts can then run against new OV instance to create a new environment. 

There are two categories of scripts
   * OV resources - those scripts are used to create OV resources including
        * Ethernet newtorks
        * Network set
        * FC / FCOE networks
        * Logical InterConnect Groups
        * Uplink Sets
        * Enclosure Groups
        * Logical Enclosures
        * Network connections
        * Local Storage connections
        * Server Profile Templates with iLO settings
        * Server Profiles with iLO settings
        
    * OV settings - the scripts are used to configure OV settings including  - STILL IN DEVELOPMENT
        * Time and Locale
        * IP address pools
        * wwnn pools
        * MAC pools


## OneView version
It works with OneView 4.20

## Prerequisites
The script requires the OneView python library at least v5.0 : https://github.com/HewlettPackard/python-hpOneView/tree/release/5.0.0-beta



## Syntax

### Configure authentication to OneView
Modify the following files:

    * oneview_config_src.json to match with your 'master' OneView instance
    * oneview_config_dest.json to match with your new (destination) OneView instance

If necessary, modify the X-API version in the json files to match with the release of OneView

    *  X-API = 1000 ---> OneView v4.20
    *  X-API = 800  ---> OneView 4.10


### To generate python scripts

```
    convertto_pyscripts.py oneview_config_src.json oneview_config_dest.json

```

