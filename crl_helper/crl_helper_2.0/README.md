# CRL HELPER_2.0 package
This document provides installation and usage of crl_helper_2.0 package. This package automatically downloads and uploads CRL’s to OneView.

## Inroduction
“crl_helper.py” is a python script that allows OneView Infrastructure administrators users to automatically download the CRL files of the CA certificates and upload them to the appliance for those CAs that are trusted in appliance. This ensures that the CRL files on the appliance are updated to the latest.
The latest CRL file on the OneView appliance ensures revocation checks using latest CRL files, on managed device certificates while communication.

## Installation Pre-requisites
1.	Ensure that python 3.5.0 or above is installed on the computer where the “crl_helper” utility will be run. The python downloads are available at https://www.python.org/downloads/. Choose the 32 bit or 64 bit versions based on the computer 
2.	Ensure that network proxy configuration is properly set up on the computer
3.	Refer to the following sub sections based on the OS you are running
	*	Run the following steps to install the python “requests” and "ldap3" packages if your computer is running with windows OS
		*	Open a command prompt
		*	Go to the directory where python is installed e.g., C:\MyPrograms\python3\
		*	Go to “Scripts” directory
		*	Run the command “pip install requests”
		*   Next Run the command "pip install ldap3"
	*	Run the following steps to install the python “requests” and "ldap3" packages if your computer is running with Linux (CentOS). Note that there may be variation of these steps based on the Linux OS variant running your computer
		*	yum install wget
		*	wget https://www.python.org/ftp/python/3.5.4/Python-3.5.4.tar.xz   (Users can choose the appropriate 3.5.0 version and above from https://www.python.org/ftp/python/)
		*	tar -xJf Python-3.5.4.tar.xz
		*	yum install gcc
		*	yum install openssl-devel 
		*	yum install zlib-devel
		*	cd Python-3.5.4
		*	./configure
		*	make
		*	make install 
		*	By now python 3.x and pip3 should have been installed
		*	Run the command "pip3 install requests --user"
		*	Next run the command "pip3 install ldap3 --user"

## Installation
1.	Windows
	*	Download the “crl_helper_2.0.zip” from the location provided by HPE
	*	Install the “crl_helper_2.0.zip” by unzipping to a desired location on your laptop/PC
	*	The unzipped file contains the files as shown in the following image
    ![](files.png)
2.  Linux (CentOS)
	*	Download the “crl_helper_2.0.tar” from the location provided by HPE
	*	Install the “crl_helper_2.0.tar” by running the following commands to a desired location on your laptop/PC
	*	tar –xvf crl_helper_2.0.tar
	*	The unzipped file contains the files as shown in the following image
    *   **Note: The commands to install the utility may vary based on the Linux OS variant present on your computer**

## 	Pre-Bundled Roots
Appliance provides the following pre-bundled CA certificates. Run the “crl_helper” utility to automatically update the CRL files issued by these appliance pre-bundled CA certificates. Refer to the next section if you want to upload CRLs for other CA certificates imported into appliance. 
	&nbsp;&nbsp;![](managecerts.png)

##  CRL Download Configuration for user imported CA certificates
Users would import their choice of CA certificates into the appliance. In order to upload CRL files for these certificates, users have to perform configuration as listed below
1.	Go to the directory/folder where the “crl_helper_2.0.zip” is extracted. Look for the file “crl_urls.json” as shown in the above section.  It has the configuration that allows automatic download of the CRLs when the “crl_helper.py” script is run
2.  This json file contains the list of all the pre-bundled CA certificates and the corresponding CRL DPs of the OneView appliance.  Users can update this json file with the details of user imported CA certificates
3.	Once a CA certificate is imported into appliance successfully, identify the certificate aliasName from the OneView appliance. Refer to the certificate management documentation in the appliance to obtain the CRL DPs for the imported certificates. 
4.	Use the CA certificate aliasName and the CRL DP obtained above, append the “crl_urls.json” file with the CA signed certificate aliasName and the DP identified. Also users can specify multiple CRL DPs in the "crl_urls.json" file. CRL is downloaded from the first accessible URL
    
	**Before appending**,</br>
	[</br>
	&nbsp;  {</br>
	&nbsp;&nbsp;	"aliasName": "Symantec Class 3 Secure Server SHA256 SSL CA",</br>
	&nbsp;&nbsp;	"CRLDps": [</br>
	&nbsp;&nbsp;&nbsp;	  "http://sg.symcb.com/sg.crl"</br>
	&nbsp;&nbsp;	]</br>
	&nbsp;  }</br>
	]</br>

    **After appending**,</br>
	**Example 1**,</br>
	[</br>
	&nbsp;  {</br>
	&nbsp;&nbsp;	"aliasName": "Symantec Class 3 Secure Server SHA256 SSL CA",</br>
	&nbsp;&nbsp;	"CRLDps": [</br>
	&nbsp;&nbsp;&nbsp;	  "http://sg.symcb.com/sg.crl"</br>
	&nbsp;&nbsp;	]</br>
	&nbsp;  },</br>
	&nbsp; {</br>
	&nbsp;&nbsp;	"aliasName": "myCAcertAliasName",</br>
	&nbsp;&nbsp;	"CRLDps": [</br>
	&nbsp;&nbsp;&nbsp;	  "http://myCAcerts.com/myCAs.crl"</br>
	&nbsp;&nbsp;	]</br>
	&nbsp;  }</br>
	]</br>
	
	**Example 2**,</br>
	[</br>
	&nbsp;  {</br>
	&nbsp;&nbsp;	"aliasName": "Symantec Class 3 Secure Server SHA256 SSL CA",</br>
	&nbsp;&nbsp;	"CRLDps": [</br>
	&nbsp;&nbsp;&nbsp;	  "http://sg.symcb.com/sg.crl"</br>
	&nbsp;&nbsp;	]</br>
	&nbsp;  },</br>
	&nbsp; {</br>
	&nbsp;&nbsp;	"aliasName": "myCAcertAliasName",</br>
	&nbsp;&nbsp;	"CRLDps": [</br>
	&nbsp;&nbsp;&nbsp;	  "ldap://ldap.myCAcert.com/CN=Certificate Authority,O=myCAcert.com?certificateRevocationList;binary"</br>
	&nbsp;&nbsp;	]</br>
	&nbsp;  }</br>
	]</br>
	
	**Example 3**,</br>
	[</br>
	&nbsp;  {</br>
	&nbsp;&nbsp;	"aliasName": "Symantec Class 3 Secure Server SHA256 SSL CA",</br>
	&nbsp;&nbsp;	"CRLDps": [</br>
	&nbsp;&nbsp;&nbsp;	  "http://sg.symcb.com/sg.crl"</br>
	&nbsp;&nbsp;	]</br>
	&nbsp;  },</br>
	&nbsp; {</br>
	&nbsp;&nbsp;	"aliasName": "myCAcertAliasName",</br>
	&nbsp;&nbsp;	"CRLDps": [</br>
	&nbsp;&nbsp;&nbsp;	  "http://myCAcerts.com/myCAs.crl",</br>
	&nbsp;&nbsp;&nbsp;	  "http://myCAcertsnew.com/myCAs.crl"</br>
	&nbsp;&nbsp;	]</br>
	&nbsp;  }</br>
	]</br>
	
	**Example 4**,</br>
	[</br>
	&nbsp;  {</br>
	&nbsp;&nbsp;	"aliasName": "Symantec Class 3 Secure Server SHA256 SSL CA",</br>
	&nbsp;&nbsp;	"CRLDps": [</br>
	&nbsp;&nbsp;&nbsp;	  "http://sg.symcb.com/sg.crl"</br>
	&nbsp;&nbsp;	]</br>
	&nbsp;  },</br>
	&nbsp; {</br>
	&nbsp;&nbsp;	"aliasName": "myCAcertAliasName",</br>
	&nbsp;&nbsp;	"CRLDps": [</br>
	&nbsp;&nbsp;&nbsp;	  "ldap://ldap.myCAcert.com/CN=Certificate Authority,O=myCAcert.com?certificateRevocationList;binary",</br>
	&nbsp;&nbsp;&nbsp;	  "http://myCAcertsnew.com/myCAs.crl"</br>
	&nbsp;&nbsp;	]</br>
	&nbsp;  }</br>
	]</br>
	
5.	Details of all the errors, processes happening while executing the script will be present in “crl_helper.log” file. 

##	Python Versions Support
1.	The “crl_helper.py” works only with python 3.5.0 and above versions
2.	On the computer running Windows, if environment variables is not set for Python 3, find the directory/folder where Python 3 has been installed. Replace “python” with path to “python3” in the following section. (e.g., C:\MyPrograms\python35\python.exe).
3.	If your computer is already installed with python 2.x version on your computer running on Linux, then follow the below instructions to run the utility
    *	Replace “python” with “python3” to run the commands as shown in the next section  

## Usage    
*	Command syntax: </br>
	Navigate in the command prompt to the directory where crl_helper.py is present.  </br>
    ```
    $>python crl_helper.py -appliance APPLIANCE -username USERNAME -password PASSWORD [-help]  [-proxy PROXYURL]
	```
	
	The following are some of the example commands to illustrate the usage of the utility.
	```
	$>python crl_helper.py -appliance 10.20.30.40 -username administrator -password admin


	$>python crl_helper.py -appliance oneview.mycompany.com -username administrator -password admin


	$>python crl_helper.py -appliance oneview.mycompany.com -username administrator -password admin -proxy http://web-proxy.mycompany.com:8080


	$>python crl_helper.py -appliance oneview.mycompany.com -username administrator -password admin -proxy http://proxyuser:proxypassword@web-proxy.myconmpany.com:8080
    
   
	$>python crl_helper.py  –appliance oneview.mycompany.com –username administrator    
              
			  
	$>python crl_helper.py  –appliance oneview.mycompany.com –username administrator –proxy http://web-proxy.mycompany.com:8080 
	```
	In the last two cases the user will be prompted for password as it is not present in the command line argument.</br>
	```
	Enter Appliance password:
    ```

## Enhancements
1.  This version supports LDAP CRL DPs
2.  This version supports multiple CRL DPs for a certificate
3.  This version works for all the OneView releases from rel/4.00 and above
4.  This version supports upload of CRLs to appliances with any locale
5.  This version supports upload of CRLs in FIPS and CNSA mode of OneView	
## 	Limitations
1.	This version of the “crl_helper.py” script supports downloading of CRL files through http and LDAP protocols only. It doesn't FTP protocol.
2.	Only anonymous bind is supported for LDAP URLs.
3.  This package works only with python 3.5.0 and above versions

## FAQs
1.  What is CRL?
    *	Certificates Authority (CA) signs the certificate
    *	CA signs the CRL file and maintains 
    *	CRL file is exposed via http/LDAP/FTP.
2.  What is CRL DP?
    *	DP -> Distribution Point
    *	Location of the CRL file is CRL DP (also known as CDP)</br>
    The CA signed leaf certificate contains the CRL DP. CRL DP is the location where the CA that signed a certificate maintains the CRL. For example, the CRL DP field you see in a CA signed leaf certificate is the location of the CRL associated with the intermediate or root CA that signed the leaf certificate. Hence to obtain a CRL DP associated with a CA, you have to look at a certificate signed by that CA

3.  What CRL DP means to appliance?
    *	During certificate import, perform revocation status of the certificate
    *	While appliance connecting to a device or remote server over SSL, perform revocation status of the incoming device certificate using the CRLs present in the appliance
