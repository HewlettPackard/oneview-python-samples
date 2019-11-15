# Generate python scripts from OneView

convertto_python_scripts.py is a python script that generates python code to configure new OneView instances. The script queries an existing OV instance (called 'Master') and based on resources and attributes configured in this instance, it will create scripts that call OV python SDK. Those scripts can then run against new OV instance to re-create the environment. 

There are two categories of scripts
   * OV resources - those scripts are used to create OV resources including
        * Ethernet newtorks
        * Network set
        * FC / FCOE networks
        * Logical InterConnect Groups
        * Uplink Sets
        * Enclosure Groups
        * Enclosures
        * Network connections
        * Local Storage connections
        * Server Profile Templates
        * Server Profiles
    * OV settings - the scripts are used to configure OV settings including  - STILL IN DEVELOPMENT
        * Time and Locale
        * IP address pools
        * WWWNN pools
        * MAC pools



## Prerequisites
Both scripts require the OneView python library at least v5.0 : https://github.com/HewlettPackard/python-hpOneView/tree/release//5.0.0-beta



## Syntax

### Configure authentication to OneView
Edit the script and modify the information here to match with your emvironment
```
CONFIG = {
    "api_version": 500,
    "ip": "192.168.1.51",
    "credentials": {
        "userName": "administrator",
        "password": "password"
    }
}

```
### To generate python scripts

```
    convertto_python_scripts.py

```

