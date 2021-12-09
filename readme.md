[comment]: # "Auto-generated SOAR connector documentation"
# Aella Data Starlight

Publisher: Aella Data  
Connector Version: 1\.6\.5  
Product Vendor: Aella Data  
Product Name: Starlight  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 4\.0\.1068  

This app integrates with an Aella Data installation to implement ingestion and investigative actions

[comment]: # "File: readme.md"
[comment]: # "Copyright (c) Aella Data Inc, 2018"
[comment]: # "This unpublished material is proprietary to Aella Data."
[comment]: # "of Aella Data."
[comment]: # ""
[comment]: # "Licensed under the Apache License, Version 2.0 (the 'License');"
[comment]: # "you may not use this file except in compliance with the License."
[comment]: # "You may obtain a copy of the License at"
[comment]: # ""
[comment]: # "    http://www.apache.org/licenses/LICENSE-2.0"
[comment]: # ""
[comment]: # "Unless required by applicable law or agreed to in writing, software distributed under"
[comment]: # "the License is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,"
[comment]: # "either express or implied. See the License for the specific language governing permissions"
[comment]: # "and limitations under the License."
[comment]: # ""
The Starlight app requires **username** and **password** parameters. When specified, the app will
end up using these for generating the basic authentication header used in the Starlight REST
endpoints.  
Connection needs be configured over HTTPS, if **test connectivity** fails please check the protocol.


### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a Starlight asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**url** |  required  | string | Starlight URL, e\.g\. https\://mystarlight\.enterprise\.com/aellaelastic
**verify\_server\_cert** |  required  | boolean | Verify Server Certificate
**username** |  required  | string | Username
**password** |  required  | password | Password
**event** |  optional  | string | Security event
**score** |  optional  | numeric | Security event severity threshold

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity\. This action logs into the device to check the connection and credentials  
[get event](#action-get-event) - Run a search query to get event on the Starlight installation based on the on\_poll result  
[on poll](#action-on-poll) - Run a query in Starlight and ingest the results  

## action: 'test connectivity'
Validate the asset configuration for connectivity\. This action logs into the device to check the connection and credentials

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'get event'
Run a search query to get event on the Starlight installation based on the on\_poll result

Type: **investigate**  
Read only: **True**

The action is to query the detailed information for the given event id, which is passed on from artifect\['id'\]

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**event\_id** |  required  | Event id to query on | string |  `starlight event id` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.data\.\*\.dstip | string | 
action\_result\.data\.\*\.dstip\_reputation | string | 
action\_result\.data\.\*\.dstport | numeric | 
action\_result\.data\.\*\.srcip | string | 
action\_result\.data\.\*\.srcip\_reputation | string | 
action\_result\.data\.\*\.srcport | numeric | 
action\_result\.data\.\*\.proto\_name | string | 
action\_result\.data\.\*\.event\_name | string | 
action\_result\.data\.\*\.event\_category | string | 
action\_result\.data\.\*\.event\_type | string | 
action\_result\.data\.\*\.\_index | string | 
action\_result\.data\.\*\.severity | numeric | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
action\_result\.parameter\.event\_id | string |  `starlight event id` 
action\_result\.data\.\*\.timed\_out | boolean |   

## action: 'on poll'
Run a query in Starlight and ingest the results

Type: **ingest**  
Read only: **True**

This will run a query in starlight using the <b>index</b>, <b>type</b>, <b>routing</b>, and <b>query</b> configured in the app settings and ingest the results\. The <b>query</b> must account for relative time between ingestion runs, query limits, and page sizes\.<br>

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**container\_id** |  optional  | Limit ingestion to these container IDs | string | 
**start\_time** |  optional  | Start of time range in epoch time \(default\: 10 days ago\) | numeric | 
**end\_time** |  optional  | End of time range in epoch time \(default\: now\) | numeric | 
**container\_count** |  optional  | Maximum number of containers to create | numeric | 
**artifact\_count** |  optional  | Maximum number of artifacts to create per container\. | numeric | 

#### Action Output
No Output